"""
Background Processing Module for ClipSense

Handles AI analysis in the background with real-time progress updates.
Uses asyncio tasks and progress tracking for efficient processing.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

try:
    from .ai_content_selector import AIContentSelector, AIContentSelectionResult
except ImportError:
    from ai_content_selector import AIContentSelector, AIContentSelectionResult

class ProcessingStatus(Enum):
    """Status of background processing"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProcessingJob:
    """Represents a background processing job"""
    job_id: str
    clips: List[str]
    music_path: str
    target_duration: int
    story_style: str
    style_preset: str
    status: ProcessingStatus
    progress: float  # 0.0 to 1.0
    current_step: str
    results: Optional[List[AIContentSelectionResult]] = None
    error: Optional[str] = None
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class BackgroundProcessor:
    """Handles background AI processing with progress tracking"""
    
    def __init__(self):
        self.ai_selector = AIContentSelector()
        self.jobs: Dict[str, ProcessingJob] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
    
    def clear_ai_cache(self):
        """Clear the AI selector cache to force fresh analysis"""
        if hasattr(self.ai_selector, '_analysis_cache'):
            self.ai_selector._analysis_cache.clear()
            print("INFO:background_processor:🧹 Cleared AI analysis cache")
        
    def create_job(self, 
                   clips: List[str], 
                   music_path: str,
                   target_duration: int = 60,
                   story_style: str = 'traditional',
                   style_preset: str = 'romantic') -> str:
        """Create a new background processing job"""
        job_id = str(uuid.uuid4())
        
        job = ProcessingJob(
            job_id=job_id,
            clips=clips,
            music_path=music_path,
            target_duration=target_duration,
            story_style=story_style,
            style_preset=style_preset,
            status=ProcessingStatus.PENDING,
            progress=0.0,
            current_step="Initializing...",
            created_at=time.time()
        )
        
        self.jobs[job_id] = job
        print(f"INFO:background_processor:📋 Created job {job_id} for {len(clips)} clips")
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get the current status of a job"""
        return self.jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status == ProcessingStatus.RUNNING:
                job.status = ProcessingStatus.CANCELLED
                print(f"INFO:background_processor:❌ Cancelled job {job_id}")
                return True
        return False
    
    async def start_processing(self, job_id: str) -> None:
        """Start processing a job in the background"""
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        job.status = ProcessingStatus.RUNNING
        job.started_at = time.time()
        job.current_step = "Starting AI analysis..."
        job.progress = 0.0
        
        print(f"INFO:background_processor:🚀 Starting job {job_id}")
        
        try:
            # Process clips in batches with progress updates
            await self._process_clips_batch(job)
            
            if job.status != ProcessingStatus.CANCELLED:
                job.status = ProcessingStatus.COMPLETED
                job.completed_at = time.time()
                job.progress = 1.0
                job.current_step = "Completed!"
                
                print(f"INFO:background_processor:✅ Job {job_id} completed in {job.completed_at - job.started_at:.2f}s")
                
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error = str(e)
            job.completed_at = time.time()
            print(f"INFO:background_processor:❌ Job {job_id} failed: {e}")
    
    async def _process_clips_batch(self, job: ProcessingJob) -> None:
        """Process clips in batches with progress updates"""
        clips = job.clips
        total_clips = len(clips)
        batch_size = 3  # Process 3 clips at a time for better performance
        
        all_results = []
        processed_count = 0
        
        # Process clips in batches
        for i in range(0, total_clips, batch_size):
            if job.status == ProcessingStatus.CANCELLED:
                break
                
            batch = clips[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_clips + batch_size - 1) // batch_size
            
            job.current_step = f"Processing batch {batch_num}/{total_batches} ({len(batch)} clips)..."
            job.progress = processed_count / total_clips
            
            print(f"INFO:background_processor:📦 Job {job.job_id}: {job.current_step}")
            
            # Process batch in parallel
            batch_tasks = []
            for clip_path in batch:
                task = self.ai_selector.analyze_clip_fast(
                    clip_path, 
                    job.story_style, 
                    job.style_preset
                )
                batch_tasks.append(task)
            
            try:
                batch_results = await asyncio.gather(*batch_tasks)
                all_results.extend(batch_results)
                processed_count += len(batch)
                
                print(f"INFO:background_processor:✅ Job {job.job_id}: Processed {processed_count}/{total_clips} clips")
                
            except Exception as e:
                print(f"INFO:background_processor:⚠️ Job {job.job_id}: Batch failed: {e}")
                # Continue with next batch
                continue
        
        # Sort results by score and select best clips
        if all_results:
            all_results.sort(key=lambda x: x.final_score, reverse=True)
            target_count = min(len(all_results), max(5, job.target_duration // 3))
            job.results = all_results[:target_count]
            
            print(f"INFO:background_processor:🎯 Job {job.job_id}: Selected {len(job.results)} best clips")
    
    def get_job_results(self, job_id: str) -> Optional[List[AIContentSelectionResult]]:
        """Get the results of a completed job"""
        job = self.jobs.get(job_id)
        if job and job.status == ProcessingStatus.COMPLETED:
            return job.results
        return None
    
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Clean up old completed jobs"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        jobs_to_remove = []
        for job_id, job in self.jobs.items():
            if (job.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED, ProcessingStatus.CANCELLED] 
                and current_time - job.created_at > max_age_seconds):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
        
        if jobs_to_remove:
            print(f"INFO:background_processor:🧹 Cleaned up {len(jobs_to_remove)} old jobs")
        
        return len(jobs_to_remove)

# Global background processor instance
background_processor = BackgroundProcessor()
