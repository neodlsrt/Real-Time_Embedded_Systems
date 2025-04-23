# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:25:23 2025

@author: delsa
"""

from math import lcm
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Recursive function to explore all valid scheduling possibilities
def schedule_jobs(jobs, current_time=0, scheduled=[], total_wait=0, missed_deadlines=None):
    global best_schedule, best_total_wait, counter

    # Initialize missed deadlines tracking for each task
    if missed_deadlines is None:
        missed_deadlines = {task["name"]: 0 for task in tasks}

    # If there are no more jobs to schedule, evaluate this schedule
    if not jobs:
        counter += 1
        if total_wait < best_total_wait:
            best_total_wait = total_wait
            best_schedule = deepcopy(scheduled)
        return
    
    # Pruning: stop exploring this path if the total wait time is already worse
    if total_wait >= best_total_wait:
        return

    # Get the list of jobs that are ready to be executed (released)
    ready = sorted([j for j in jobs if j["release"] <= current_time], key=lambda j: j["deadline"])

    # If no jobs are ready, fast-forward to the next job's release time
    if not ready:
        next_time = min(j["release"] for j in jobs)
        schedule_jobs(jobs, next_time, scheduled, total_wait)
        return

    # Try scheduling each ready job next
    for job in ready:
        start = current_time
        end = start + job["execution"]
  
        # Check if this job would miss its deadline
        if end > job["deadline"]:
            # If the task is not allowed to miss a deadline, skip it
            if not any(t["name"] == job["task"] and t.get("missable", False) for t in tasks):
                continue
            # If it already missed a deadline before, skip it because we accept only 1 miss
            if missed_deadlines[job["task"]] >= 1:
                continue


        wait = start - job["release"]
        
        # Update job list and mark it as scheduled
        new_jobs = jobs.copy()
        new_jobs.remove(job)
        scheduled.append({**job, "start": start})
        
        # Track missed deadline if applicable
        if end > job["deadline"]:
            missed_deadlines[job["task"]] += 1
            
        # Recursive call with the updated state
        schedule_jobs(new_jobs, end, scheduled, total_wait + wait, missed_deadlines)
        
        # Backtrack: remove job from schedule and undo deadline tracking
        scheduled.pop()
        if end > job["deadline"]:
            missed_deadlines[job["task"]] -= 1
        
# Function to plot a Gantt chart of the schedule
def plot_gantt(schedule):
    fig, ax = plt.subplots(figsize=(10, 2))

    y = 0
    colors = {}

    for job in schedule:
        start = job["start"]
        end = start + job["execution"]
        label = job["task"]

        if label not in colors:
            colors[label] = f"C{len(colors)}"
            
        # Draw job rectangle
        rect = patches.Rectangle((start, y), job["execution"], 0.6,
                                 edgecolor="black", facecolor=colors[label])
        ax.add_patch(rect)
        
        # Display job label
        ax.text(start + job["execution"]/2, y + 0.3, label, ha="center", va="center", color="white", fontsize=9)

    ax.set_xlim(0, lcm(*[task["T"] for task in tasks]))
    ax.set_ylim(0, 1)
    ax.set_xlabel("Temps")
    ax.set_yticks([])
    plt.tight_layout()
    plt.show()


#%% Task definitions

tasks = [
    {"name": "τ1", "C": 2, "T": 10, "missable": False},
    {"name": "τ2", "C": 3, "T": 10, "missable": False},
    {"name": "τ3", "C": 2, "T": 20, "missable": False},
    {"name": "τ4", "C": 2, "T": 20, "missable": False},
    {"name": "τ5", "C": 2, "T": 40, "missable": False},  # this task is allowed to miss deadlines
    {"name": "τ6", "C": 2, "T": 40, "missible": False},
    {"name": "τ7", "C": 3, "T": 80, "missible": False},
]
 
# Compute total CPU utilization
Utilization = np.sum([i["C"] / i["T"] for i in tasks])

if Utilization < 1:
    
    print("It is schedulable because Utilization = ",Utilization)
    
    # Compute hyperperiod (LCM of all periods)
    H = lcm(*[task["T"] for task in tasks])
    print(f"Hyperpériod = {H}")
    
    # Generate all job instances over the hyperperiod
    jobs = []
    for task in tasks:
        for t in range(0, H, task["T"]):
            jobs.append({
                "task": task["name"],
                "release": t,
                "deadline": t + task["T"],
                "execution": task["C"]
            })
    
    # Sort jobs by release time
    jobs.sort(key=lambda j: j["release"])
    
    # Initialize global best schedule tracking
    best_schedule = None
    best_total_wait = float("inf")
    counter = 0  
    
    # Start the scheduling search
    schedule_jobs(jobs)
    # Plot the final schedule
    plot_gantt(best_schedule)
    
    # Print the best schedule found
    print("\n🏆 Best schedule found:")
    for job in best_schedule:
        print(f'{job["task"]} : {job["start"]} → {job["start"] + job["execution"]} (wait: {job["start"] - job["release"]})')

    print(f"Total waiting time = {best_total_wait}")
    print(f"\nTotal number of schedules tested = {counter}")