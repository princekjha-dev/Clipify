"""
Folder-Based Workflow for Clipify
Drop video files into input folder → Automatically process → Output clips

Supports:
- Real-time folder monitoring
- Batch processing
- Auto-retry on failure
- Progress tracking
- Automatic cleanup
"""

import os
import time
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
from threading import Thread
import subprocess

from utils.logger import Logger
from utils.errors import ClipifyError


class FolderWorkflow:
    """Manages video processing from input folder to output folder"""
    
    SUPPORTED_FORMATS = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.flv', '.m4v'}
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 5  # seconds
    
    def __init__(
        self,
        input_folder: Path = None,
        output_folder: Path = None,
        auto_cleanup: bool = True,
        logger: Logger = None
    ):
        """
        Initialize folder workflow
        
        Args:
            input_folder: Folder to watch for videos (default: ./input)
            output_folder: Folder to save clips (default: ./output)
            auto_cleanup: Delete source video after successful processing
            logger: Logger instance
        """
        self.input_folder = input_folder or Path("./input")
        self.output_folder = output_folder or Path("./output")
        self.auto_cleanup = auto_cleanup
        self.logger = logger or Logger()
        
        # Create folders if they don't exist
        self.input_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Status tracking
        self.processing_state = {}  # video_path -> status
        self.failed_videos = []
        
    def get_pending_videos(self) -> List[Path]:
        """Get list of unprocessed videos in input folder"""
        videos = []
        
        for file_path in self.input_folder.glob("*"):
            # Skip if already processing or failed
            if file_path in self.processing_state or file_path in self.failed_videos:
                continue
            
            # Check if video file
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                videos.append(file_path)
        
        return sorted(videos)
    
    def process_video(
        self,
        video_path: Path,
        process_func: Callable,
        **kwargs
    ) -> Dict:
        """
        Process a single video file
        
        Args:
            video_path: Path to video file
            process_func: Function to call with (video_path, logger, **kwargs)
            **kwargs: Additional arguments to pass to process_func
        
        Returns:
            Dict with processing results or error info
        """
        
        self.logger.info(f"Processing: {video_path.name}")
        self.processing_state[video_path] = "in_progress"
        
        attempt = 0
        last_error = None
        
        while attempt < self.RETRY_ATTEMPTS:
            try:
                attempt += 1
                
                if attempt > 1:
                    self.logger.info(f"  Retry {attempt}/{self.RETRY_ATTEMPTS}")
                    time.sleep(self.RETRY_DELAY)
                
                # Call processing function
                results = process_func(video_path, self.logger, **kwargs)
                
                # Success
                self.processing_state[video_path] = "completed"
                
                # Move clips to output
                if results.get('clips'):
                    self._move_clips_to_output(
                        results['clips'],
                        video_path.stem
                    )
                
                # Auto-cleanup source video if requested
                if self.auto_cleanup:
                    try:
                        video_path.unlink()
                        self.logger.info(f"  Cleaned up source: {video_path.name}")
                    except Exception as e:
                        self.logger.warning(f"  Could not delete source: {e}")
                
                return {
                    'success': True,
                    'video': str(video_path),
                    'results': results
                }
            
            except Exception as e:
                last_error = str(e)
                
                if attempt < self.RETRY_ATTEMPTS:
                    self.logger.warning(f"  Error (will retry): {e}")
                else:
                    self.logger.error(f"  Failed after {attempt} attempts: {e}")
        
        # All retries exhausted
        self.processing_state[video_path] = "failed"
        self.failed_videos.append(video_path)
        
        return {
            'success': False,
            'video': str(video_path),
            'error': last_error,
            'attempts': attempt
        }
    
    def process_batch(
        self,
        process_func: Callable,
        max_videos: int = None,
        **kwargs
    ) -> List[Dict]:
        """
        Process all pending videos in batch
        
        Args:
            process_func: Processing function
            max_videos: Maximum videos to process (None = all)
            **kwargs: Arguments to pass to process_func
        
        Returns:
            List of processing results
        """
        
        videos = self.get_pending_videos()
        
        if max_videos:
            videos = videos[:max_videos]
        
        if not videos:
            self.logger.info("No pending videos")
            return []
        
        self.logger.header(f"Processing {len(videos)} video(s)")
        
        results = []
        
        for i, video_path in enumerate(videos, 1):
            self.logger.step(i, len(videos), f"Processing {video_path.name}")
            
            result = self.process_video(video_path, process_func, **kwargs)
            results.append(result)
            
            if result['success']:
                self.logger.success(f"✓ Completed: {video_path.name}")
            else:
                self.logger.error(f"✗ Failed: {video_path.name}")
        
        # Summary
        completed = sum(1 for r in results if r['success'])
        failed = len(results) - completed
        
        self.logger.header("BATCH PROCESSING COMPLETE")
        self.logger.info(f"Completed: {completed}/{len(results)}")
        if failed > 0:
            self.logger.warning(f"Failed: {failed}/{len(results)}")
        
        return results
    
    def process_watch(
        self,
        process_func: Callable,
        poll_interval: int = 10,
        max_workers: int = 1,
        **kwargs
    ):
        """
        Watch input folder and process videos as they arrive (daemon mode)
        
        Args:
            process_func: Processing function
            poll_interval: Check folder every N seconds
            max_workers: Number of parallel workers
            **kwargs: Arguments to pass to process_func
        """
        
        self.logger.header("CLIPIFY FOLDER WATCHER")
        self.logger.info(f"Input folder: {self.input_folder.absolute()}")
        self.logger.info(f"Output folder: {self.output_folder.absolute()}")
        self.logger.info(f"Poll interval: {poll_interval}s")
        self.logger.info(f"Workers: {max_workers}")
        self.logger.info("Waiting for videos... (Ctrl+C to stop)")
        self.logger.header("")
        
        try:
            while True:
                videos = self.get_pending_videos()
                
                if videos:
                    for video_path in videos[:max_workers]:
                        # Process in thread if parallel
                        if max_workers > 1:
                            thread = Thread(
                                target=self.process_video,
                                args=(video_path, process_func),
                                kwargs=kwargs
                            )
                            thread.daemon = True
                            thread.start()
                        else:
                            self.process_video(video_path, process_func, **kwargs)
                
                time.sleep(poll_interval)
        
        except KeyboardInterrupt:
            self.logger.info("\nWatcher stopped")
    
    def _move_clips_to_output(self, clip_paths: List[Path], video_stem: str):
        """Move extracted clips to output folder"""
        
        # Create subfolder for this video's clips
        video_output = self.output_folder / video_stem
        video_output.mkdir(parents=True, exist_ok=True)
        
        for clip_path in clip_paths:
            if clip_path.exists():
                try:
                    dest = video_output / clip_path.name
                    shutil.move(str(clip_path), str(dest))
                except Exception as e:
                    self.logger.warning(f"Could not move {clip_path.name}: {e}")
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        
        pending = len(self.get_pending_videos())
        in_progress = sum(1 for s in self.processing_state.values() if s == "in_progress")
        completed = sum(1 for s in self.processing_state.values() if s == "completed")
        failed = len(self.failed_videos)
        
        return {
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'failed': failed,
            'total_processed': completed + failed
        }
    
    def save_status(self, path: Path = None):
        """Save processing status to file"""
        
        path = path or self.output_folder / "processing_status.json"
        
        status = self.get_status()
        status['timestamp'] = datetime.now().isoformat()
        
        with open(path, 'w') as f:
            json.dump(status, f, indent=2)
        
        return path
    
    def cleanup_failed(self):
        """Move failed videos to subfolder for review"""
        
        if not self.failed_videos:
            return
        
        failed_folder = self.input_folder / "_failed"
        failed_folder.mkdir(exist_ok=True)
        
        for video_path in self.failed_videos:
            if video_path.exists():
                try:
                    shutil.move(str(video_path), str(failed_folder / video_path.name))
                    self.logger.info(f"Moved to _failed: {video_path.name}")
                except Exception as e:
                    self.logger.warning(f"Could not move failed video: {e}")
    
    def export_manifest(self, path: Path = None) -> Path:
        """Export processing manifest with all clips and metadata"""
        
        path = path or self.output_folder / "manifest.json"
        
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'input_folder': str(self.input_folder),
            'output_folder': str(self.output_folder),
            'videos': []
        }
        
        # Collect all output videos and their clips
        for video_folder in self.output_folder.iterdir():
            if video_folder.is_dir() and not video_folder.name.startswith('_'):
                clips = list(video_folder.glob("*.mp4"))
                if clips:
                    manifest['videos'].append({
                        'name': video_folder.name,
                        'clips': [
                            {
                                'name': c.name,
                                'size_mb': c.stat().st_size / (1024 * 1024),
                                'path': str(c)
                            }
                            for c in sorted(clips)
                        ]
                    })
        
        with open(path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return path


def create_folder_workflow(
    input_dir: str = "input",
    output_dir: str = "output",
    logger: Logger = None
) -> FolderWorkflow:
    """
    Create folder workflow with standard configuration
    
    Args:
        input_dir: Input folder path
        output_dir: Output folder path
        logger: Logger instance
    
    Returns:
        FolderWorkflow instance
    """
    
    return FolderWorkflow(
        input_folder=Path(input_dir),
        output_folder=Path(output_dir),
        auto_cleanup=True,
        logger=logger
    )
