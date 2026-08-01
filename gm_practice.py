#!/usr/bin/env python3
"""
Coding Prep - Local Practice Runner
================================================

Runs entirely on your own Python. No browser, no internet, no dependencies.

QUICK START
-----------
    python3 gm_practice.py list                 # see all problems
    python3 gm_practice.py start two-sum        # create a solution file to edit
    python3 gm_practice.py test two-sum         # run the test cases
    python3 gm_practice.py trace two-sum        # LINE-BY-LINE walkthrough of YOUR code
    python3 gm_practice.py trace two-sum --solution   # walkthrough of the official solution
    python3 gm_practice.py hint two-sum         # nudge, not the answer
    python3 gm_practice.py solution two-sum     # full solution + explanation
    python3 gm_practice.py progress             # what you've solved

Your work is saved in ./gm_solutions/ as ordinary .py files, so you can edit
them in VS Code or any editor you like.
"""

import sys
import os
import io
import json
import contextlib
import traceback

SOLUTIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gm_solutions")
PROGRESS_FILE = os.path.join(SOLUTIONS_DIR, ".progress.json")

# ANSI colors (disabled automatically when piping to a file)
class C:
    on = sys.stdout.isatty()
    G = "\033[32m" if on else ""
    R = "\033[31m" if on else ""
    Y = "\033[33m" if on else ""
    B = "\033[34m" if on else ""
    DIM = "\033[2m" if on else ""
    BOLD = "\033[1m" if on else ""
    HL = "\033[43;30m" if on else ""   # highlighted line
    OFF = "\033[0m" if on else ""


# ============================================================================
# PROBLEMS
# ============================================================================

PROBLEMS = {
"two-sum": {
    "name": "Two Sum",
    "diff": "Easy",
    "group": "Hash Maps & Arrays",
    "prompt": """Given an array of integers `nums` and an integer `target`, return the
indices of the two numbers that add up to `target`.

Exactly one valid answer exists. Return the indices in ascending order.

    two_sum([2,7,11,15], 9)  ->  [0, 1]""",
    "starter": "def two_sum(nums, target):\n    # your code here\n    pass\n",
    "tests": [
        ("two_sum([2,7,11,15], 9)", [0, 1]),
        ("two_sum([3,2,4], 6)", [1, 2]),
        ("two_sum([3,3], 6)", [0, 1]),
        ("two_sum([-1,-2,-3,-4,-5], -8)", [2, 4]),
    ],
    "hint": "Brute force is two nested loops, O(n^2). For O(n): as you walk the array "
            "once, what would you need stored to know instantly whether the complement "
            "(target - num) appeared earlier?",
    "solution": '''def two_sum(nums, target):
    seen = {}                      # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []''',
    "explain": "One pass, storing each value's index as you go. Dict lookup is O(1), so the "
               "whole scan is O(n). Say the brute force out loud first, then present this as "
               "the optimization - interviewers want the trade-off reasoning.",
    "cx": "Time O(n) | Space O(n)",
},

"group-anagrams": {
    "name": "Group Anagrams",
    "diff": "Medium",
    "group": "Hash Maps & Arrays",
    "prompt": """Group the anagrams together. Return groups sorted by their first element,
with each group's words in their original relative order.

    group_anagrams(["eat","tea","tan","ate","nat","bat"])
      ->  [['bat'], ['eat', 'tea', 'ate'], ['tan', 'nat']]""",
    "starter": "def group_anagrams(strs):\n    # your code here\n    pass\n",
    "tests": [
        ('group_anagrams(["eat","tea","tan","ate","nat","bat"])',
         [['bat'], ['eat', 'tea', 'ate'], ['tan', 'nat']]),
        ('group_anagrams([""])', [['']]),
        ('group_anagrams(["abc","cba","xyz"])', [['abc', 'cba'], ['xyz']]),
    ],
    "hint": "Two words are anagrams if they share a canonical form. Sorted letters work "
            "('eat' and 'tea' both become 'aet'). A character-count tuple also works and "
            "avoids the sort.",
    "solution": '''from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        key = tuple(sorted(word))       # canonical form
        groups[key].append(word)
    return sorted(groups.values())''',
    "explain": "Bucket each word under a canonical key. Sorting each word is O(k log k), so "
               "total is O(n*k log k). The counting-tuple variant drops it to O(n*k) - mention "
               "it as a follow-up optimization.",
    "cx": "Time O(n*k log k) | Space O(n*k)",
},

"top-k-frequent": {
    "name": "Top K Frequent Elements",
    "diff": "Medium",
    "group": "Hash Maps & Arrays",
    "prompt": """Return the k most frequent elements, ordered most frequent first.

    top_k_frequent([1,1,1,2,2,3], 2)  ->  [1, 2]""",
    "starter": "def top_k_frequent(nums, k):\n    # your code here\n    pass\n",
    "tests": [
        ("top_k_frequent([1,1,1,2,2,3], 2)", [1, 2]),
        ("top_k_frequent([1], 1)", [1]),
        ("top_k_frequent([4,4,4,5,5,6,6,6,6], 3)", [6, 4, 5]),
    ],
    "hint": "Counting is easy. For selecting top k: a full sort is O(n log n), a heap of "
            "size k is O(n log k), bucket sort by frequency is O(n). Know all three.",
    "solution": '''from collections import Counter
import heapq

def top_k_frequent(nums, k):
    counts = Counter(nums)
    return [v for v, _ in heapq.nlargest(k, counts.items(), key=lambda kv: kv[1])]''',
    "explain": "Counter gives frequencies in O(n); the heap is O(n log k), beating a sort when "
               "k is small. Bucket sort hits O(n) since a frequency can never exceed n - that "
               "observation is the senior-level answer.",
    "cx": "Time O(n log k) | Space O(n)",
},

"product-except-self": {
    "name": "Product of Array Except Self",
    "diff": "Medium",
    "group": "Hash Maps & Arrays",
    "prompt": """Return an array where each element is the product of every other element.
No division, O(n) time.

    product_except_self([1,2,3,4])  ->  [24, 12, 8, 6]""",
    "starter": "def product_except_self(nums):\n    # your code here\n    pass\n",
    "tests": [
        ("product_except_self([1,2,3,4])", [24, 12, 8, 6]),
        ("product_except_self([-1,1,0,-3,3])", [0, 0, 9, 0, 0]),
        ("product_except_self([2,3])", [3, 2]),
    ],
    "hint": "The answer at index i is (product of everything left) x (product of everything "
            "right). Can you compute both with two sweeps?",
    "solution": '''def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    prefix = 1
    for i in range(n):                 # left sweep
        result[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):     # right sweep
        result[i] *= suffix
        suffix *= nums[i]
    return result''',
    "explain": "Two sweeps: left-to-right for prefix products, right-to-left for suffix. The "
               "output array doesn't count as extra space by convention, so O(1) auxiliary. "
               "Zero-handling falls out naturally, which is why this beats the division trick.",
    "cx": "Time O(n) | Space O(1) auxiliary",
},

"longest-consecutive": {
    "name": "Longest Consecutive Sequence",
    "diff": "Medium",
    "group": "Hash Maps & Arrays",
    "prompt": """Return the length of the longest run of consecutive integers. Aim for O(n).

    longest_consecutive([100,4,200,1,3,2])  ->  4""",
    "starter": "def longest_consecutive(nums):\n    # your code here\n    pass\n",
    "tests": [
        ("longest_consecutive([100,4,200,1,3,2])", 4),
        ("longest_consecutive([0,3,7,2,5,8,4,6,0,1])", 9),
        ("longest_consecutive([])", 0),
        ("longest_consecutive([1,1,1])", 1),
    ],
    "hint": "Sorting gives O(n log n) - they'll push for better. Put everything in a set, "
            "then only start counting a run from a number that has no predecessor.",
    "solution": '''def longest_consecutive(nums):
    num_set = set(nums)
    best = 0
    for num in num_set:
        if num - 1 in num_set:
            continue                 # not the start of a run - skip
        length = 1
        while num + length in num_set:
            length += 1
        best = max(best, length)
    return best''',
    "explain": "The 'skip if predecessor exists' guard is what makes this O(n): each run is "
               "walked once from its true starting point. Without it you'd re-walk the same "
               "run from every member. Call out that guard explicitly in an interview.",
    "cx": "Time O(n) | Space O(n)",
},

"longest-substring": {
    "name": "Longest Substring Without Repeating Characters",
    "diff": "Medium",
    "group": "Two Pointers & Sliding Window",
    "prompt": """Return the length of the longest substring with no repeated characters.

    length_of_longest_substring("abcabcbb")  ->  3""",
    "starter": "def length_of_longest_substring(s):\n    # your code here\n    pass\n",
    "tests": [
        ('length_of_longest_substring("abcabcbb")', 3),
        ('length_of_longest_substring("bbbbb")', 1),
        ('length_of_longest_substring("pwwkew")', 3),
        ('length_of_longest_substring("")', 0),
        ('length_of_longest_substring("dvdf")', 3),
    ],
    "hint": "Sliding window with two pointers. When the right pointer hits a character "
            "already in the window, jump the left pointer past that character's last "
            "occurrence - don't step one at a time.",
    "solution": '''def length_of_longest_substring(s):
    last_seen = {}
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1     # jump past the duplicate
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best''',
    "explain": "The guard last_seen[ch] >= left matters: a stale index from before the window "
               "must not drag left backward. The 'dvdf' test case catches exactly that bug - "
               "without the guard it returns 2 instead of 3.",
    "cx": "Time O(n) | Space O(min(n, charset))",
},

"container-water": {
    "name": "Container With Most Water",
    "diff": "Medium",
    "group": "Two Pointers & Sliding Window",
    "prompt": """Find two lines that with the x-axis hold the most water. Return the max area.

    max_area([1,8,6,2,5,4,8,3,7])  ->  49""",
    "starter": "def max_area(heights):\n    # your code here\n    pass\n",
    "tests": [
        ("max_area([1,8,6,2,5,4,8,3,7])", 49),
        ("max_area([1,1])", 1),
        ("max_area([4,3,2,1,4])", 16),
        ("max_area([1,2,1])", 2),
    ],
    "hint": "Start at both ends - the widest container. Moving the taller pointer can never "
            "help, since area is capped by the shorter line. So which pointer moves?",
    "solution": '''def max_area(heights):
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        height = min(heights[left], heights[right])
        best = max(best, height * (right - left))
        if heights[left] < heights[right]:
            left += 1          # only moving the shorter side can help
        else:
            right -= 1
    return best''',
    "explain": "Say the justification out loud: width always shrinks as you move inward, so "
               "the only way to gain area is a taller limiting line - and the limit is the "
               "shorter one. That argument is why the greedy move is correct, not just fast.",
    "cx": "Time O(n) | Space O(1)",
},

"merge-intervals": {
    "name": "Merge Intervals",
    "diff": "Medium",
    "group": "Intervals",
    "prompt": """Merge all overlapping intervals, returning the result sorted by start time.

    merge([[1,3],[2,6],[8,10],[15,18]])  ->  [[1, 6], [8, 10], [15, 18]]""",
    "starter": "def merge(intervals):\n    # your code here\n    pass\n",
    "tests": [
        ("merge([[1,3],[2,6],[8,10],[15,18]])", [[1, 6], [8, 10], [15, 18]]),
        ("merge([[1,4],[4,5]])", [[1, 5]]),
        ("merge([])", []),
        ("merge([[1,4],[2,3]])", [[1, 4]]),
    ],
    "hint": "Sort by start time first. Then walk through: either the interval overlaps the "
            "last merged one (extend it) or it doesn't (append it). Watch the nested case "
            "[[1,4],[2,3]].",
    "solution": '''def merge(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:            # overlaps
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged''',
    "explain": "The max() is essential - without it a fully nested interval like [2,3] inside "
               "[1,4] would wrongly shrink the end to 3. This pattern shows up constantly in "
               "scheduling and telemetry-windowing questions.",
    "cx": "Time O(n log n) | Space O(n)",
},

"insert-interval": {
    "name": "Insert Interval",
    "diff": "Medium",
    "group": "Intervals",
    "prompt": """Given sorted non-overlapping intervals, insert a new interval and merge
where necessary.

    insert([[1,3],[6,9]], [2,5])  ->  [[1, 5], [6, 9]]""",
    "starter": "def insert(intervals, new_interval):\n    # your code here\n    pass\n",
    "tests": [
        ("insert([[1,3],[6,9]], [2,5])", [[1, 5], [6, 9]]),
        ("insert([[1,2],[3,5],[6,7],[8,10],[12,16]], [4,8])", [[1, 2], [3, 10], [12, 16]]),
        ("insert([], [5,7])", [[5, 7]]),
        ("insert([[1,5]], [6,8])", [[1, 5], [6, 8]]),
    ],
    "hint": "Three phases: intervals entirely before, intervals that overlap (absorb them), "
            "then everything after. Input is already sorted, so this is O(n) - don't re-sort.",
    "solution": '''def insert(intervals, new_interval):
    result = []
    start, end = new_interval
    i, n = 0, len(intervals)

    while i < n and intervals[i][1] < start:      # phase 1: before
        result.append(intervals[i]); i += 1

    while i < n and intervals[i][0] <= end:       # phase 2: absorb overlaps
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1]); i += 1
    result.append([start, end])

    while i < n:                                   # phase 3: after
        result.append(intervals[i]); i += 1
    return result''',
    "explain": "Three explicit phases keep the conditionals clean and are far easier to "
               "explain on a whiteboard than one branching loop. Because the input is "
               "pre-sorted you get O(n) - point that out, candidates often re-sort by habit.",
    "cx": "Time O(n) | Space O(n)",
},

"meeting-rooms": {
    "name": "Meeting Rooms II",
    "diff": "Medium",
    "group": "Intervals",
    "prompt": """Return the minimum number of conference rooms required.

    min_meeting_rooms([[0,30],[5,10],[15,20]])  ->  2""",
    "starter": "def min_meeting_rooms(intervals):\n    # your code here\n    pass\n",
    "tests": [
        ("min_meeting_rooms([[0,30],[5,10],[15,20]])", 2),
        ("min_meeting_rooms([[7,10],[2,4]])", 1),
        ("min_meeting_rooms([])", 0),
        ("min_meeting_rooms([[1,5],[2,6],[3,7],[4,8]])", 4),
        ("min_meeting_rooms([[1,2],[2,3],[3,4]])", 1),
    ],
    "hint": "Sort by start time and keep a min-heap of end times. The root is the room "
            "freeing up soonest - if the next meeting starts at or after it, reuse that room. "
            "The heap's size is the answer.",
    "solution": '''import heapq

def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])
    end_times = []                       # min-heap of room end times
    for start, end in intervals:
        if end_times and end_times[0] <= start:
            heapq.heapreplace(end_times, end)   # reuse the freed room
        else:
            heapq.heappush(end_times, end)      # open a new room
    return len(end_times)''',
    "explain": "The classic resource-allocation pattern - it maps onto connection limits, "
               "worker-pool sizing, and rate limiting. The <= matters: a meeting ending exactly "
               "when the next starts frees the room. Expect a probe on that boundary.",
    "cx": "Time O(n log n) | Space O(n)",
},

"valid-parens": {
    "name": "Valid Parentheses",
    "diff": "Easy",
    "group": "Stacks & Queues",
    "prompt": """Given a string of ()[]{}, determine whether the brackets are balanced and
properly nested.

    is_valid("()[]{}")  ->  True
    is_valid("(]")      ->  False""",
    "starter": "def is_valid(s):\n    # your code here\n    pass\n",
    "tests": [
        ('is_valid("()")', True),
        ('is_valid("()[]{}")', True),
        ('is_valid("(]")', False),
        ('is_valid("([)]")', False),
        ('is_valid("{[]}")', True),
        ('is_valid("(")', False),
        ('is_valid("")', True),
    ],
    "hint": "Push opening brackets onto a stack. On a closing bracket, the stack top must be "
            "its match. Two failure modes at the end: leftover openers, and a closer arriving "
            "on an empty stack.",
    "solution": '''def is_valid(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs:                       # closing bracket
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:                                 # opening bracket
            stack.append(ch)
    return not stack                          # leftovers mean unbalanced''',
    "explain": "Easy, but often the warm-up before something harder, so execute it cleanly and "
               "quickly. The two edge cases people miss are the empty-stack pop and the "
               "trailing unclosed opener - handle both explicitly and say so as you code.",
    "cx": "Time O(n) | Space O(n)",
},

"daily-temps": {
    "name": "Daily Temperatures",
    "diff": "Medium",
    "group": "Stacks & Queues",
    "prompt": """Return how many days you'd wait for a warmer temperature. Use 0 where none.

    daily_temperatures([73,74,75,71,69,72,76,73])
      ->  [1, 1, 4, 2, 1, 1, 0, 0]""",
    "starter": "def daily_temperatures(temps):\n    # your code here\n    pass\n",
    "tests": [
        ("daily_temperatures([73,74,75,71,69,72,76,73])", [1, 1, 4, 2, 1, 1, 0, 0]),
        ("daily_temperatures([30,40,50,60])", [1, 1, 1, 0]),
        ("daily_temperatures([50,50,50])", [0, 0, 0]),
    ],
    "hint": "Keep a stack of indices whose answer is still unknown, with temperatures "
            "decreasing. When a warmer day arrives, it resolves every colder index on top.",
    "solution": '''def daily_temperatures(temps):
    result = [0] * len(temps)
    stack = []                       # indices, temps decreasing
    for i, temp in enumerate(temps):
        while stack and temps[stack[-1]] < temp:
            prev = stack.pop()
            result[prev] = i - prev
        stack.append(i)
    return result''',
    "explain": "The monotonic stack pattern - recognize it whenever a problem asks for the "
               "'next greater/smaller element'. Each index is pushed and popped at most once, "
               "so despite the nested while loop it's O(n). State that amortized argument "
               "explicitly; interviewers check whether you know why it isn't quadratic.",
    "cx": "Time O(n) | Space O(n)",
},

"num-islands": {
    "name": "Number of Islands",
    "diff": "Medium",
    "group": "Trees & Graphs",
    "prompt": """Count islands in a grid of '1' (land) and '0' (water), connected
horizontally or vertically.

    num_islands([["1","1","0"],["1","0","0"],["0","0","1"]])  ->  2""",
    "starter": "def num_islands(grid):\n    # your code here\n    pass\n",
    "tests": [
        ('num_islands([["1","1","0"],["1","0","0"],["0","0","1"]])', 2),
        ('num_islands([["1","1","1"],["1","1","1"]])', 1),
        ('num_islands([["0","0"],["0","0"]])', 0),
        ('num_islands([])', 0),
        ('num_islands([["1","0","1","0","1"]])', 3),
    ],
    "hint": "Scan every cell. Unvisited land means a new island; then flood-fill (BFS or DFS) "
            "to mark its entire connected region so you never count it twice.",
    "solution": '''from collections import deque

def num_islands(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != '1':
                continue
            count += 1
            queue = deque([(r, c)])
            grid[r][c] = '0'                    # mark on enqueue
            while queue:
                cr, cc = queue.popleft()
                for dr, dc in ((1,0), (-1,0), (0,1), (0,-1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                        grid[nr][nc] = '0'
                        queue.append((nr, nc))
    return count''',
    "explain": "BFS over DFS is a deliberate choice worth voicing: recursive DFS can blow the "
               "stack on a large all-land grid. Mark cells the moment you enqueue them, not "
               "when you dequeue, or the same cell enters the queue twice.",
    "cx": "Time O(rows*cols) | Space O(rows*cols)",
},

"course-schedule": {
    "name": "Course Schedule",
    "diff": "Medium",
    "group": "Trees & Graphs",
    "prompt": """Prerequisites are pairs [a, b] meaning b must come before a. Return whether
all courses can be finished.

    can_finish(2, [[1,0]])         ->  True
    can_finish(2, [[1,0],[0,1]])   ->  False   (cycle)""",
    "starter": "def can_finish(num_courses, prerequisites):\n    # your code here\n    pass\n",
    "tests": [
        ("can_finish(2, [[1,0]])", True),
        ("can_finish(2, [[1,0],[0,1]])", False),
        ("can_finish(4, [[1,0],[2,1],[3,2]])", True),
        ("can_finish(3, [[0,1],[1,2],[2,0]])", False),
        ("can_finish(1, [])", True),
    ],
    "hint": "This is cycle detection in a directed graph. Kahn's algorithm: repeatedly remove "
            "nodes with zero remaining prerequisites. If you can't process everything, there "
            "is a cycle.",
    "solution": '''from collections import deque, defaultdict

def can_finish(num_courses, prerequisites):
    graph = defaultdict(list)        # prereq -> [courses it unlocks]
    in_degree = [0] * num_courses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(c for c in range(num_courses) if in_degree[c] == 0)
    completed = 0
    while queue:
        course = queue.popleft()
        completed += 1
        for nxt in graph[course]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)
    return completed == num_courses  # short of n means a cycle''',
    "explain": "Kahn's algorithm generalizes far beyond courses - build dependencies, service "
               "startup ordering, pipeline DAGs. Worth connecting to circular microservice "
               "dependencies in an interview. Returning the actual order is the usual follow-up.",
    "cx": "Time O(V + E) | Space O(V + E)",
},

"lru-cache": {
    "name": "LRU Cache",
    "diff": "Medium",
    "group": "Design",
    "prompt": """Fixed-capacity cache with O(1) get and put, evicting the least recently used
entry. get returns -1 if the key is missing.

*** Practice until you can write this cold in 15 minutes. It is the single most
common senior-level coding question. ***

    c = LRUCache(2)
    c.put(1,1); c.put(2,2)
    c.get(1)     ->  1
    c.put(3,3)               # evicts key 2
    c.get(2)     ->  -1""",
    "starter": """class LRUCache:
    def __init__(self, capacity):
        pass

    def get(self, key):
        pass

    def put(self, key, value):
        pass
""",
    "tests": [
        ("""(lambda: (
    lambda c: [c.put(1,1), c.put(2,2), c.get(1), c.put(3,3), c.get(2),
               c.put(4,4), c.get(1), c.get(3), c.get(4)]
)(LRUCache(2)))()""", [None, None, 1, None, -1, None, -1, 3, 4]),
        ("(lambda c: [c.put(1,1), c.put(2,2), c.get(1), c.get(2)])(LRUCache(1))",
         [None, None, -1, 2]),
        ("(lambda c: [c.put(1,1), c.put(1,10), c.get(1)])(LRUCache(2))", [None, None, 10]),
        ("(lambda c: [c.get(99)])(LRUCache(2))", [-1]),
    ],
    "hint": "You need O(1) lookup AND O(1) reordering. A dict gives the first; a doubly "
            "linked list gives the second. Store the node itself as the dict value so you can "
            "unlink it instantly. OrderedDict does both - but be ready to hand-roll it.",
    "solution": '''from collections import OrderedDict

class LRUCache:
    """Version 1 - use this if the standard library is allowed."""
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)          # mark as most recently used
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)   # evict least recently used


# Version 2 - hand-rolled doubly linked list. PRACTICE THIS ONE.
class Node:
    __slots__ = ('key', 'val', 'prev', 'next')
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCacheManual:
    def __init__(self, capacity):
        self.capacity = capacity
        self.map = {}                        # key -> Node
        self.head, self.tail = Node(), Node()   # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _add_front(self, node):
        node.next, node.prev = self.head.next, self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node); self._add_front(node)   # using it makes it newest
        return node.val

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self.map[key] = node
        self._add_front(node)
        if len(self.map) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]            # DO NOT FORGET THIS LINE''',
    "explain": "Two things sink candidates. First: forgetting to delete the evicted key from "
               "the dict, which leaks memory and corrupts future lookups. Second: fumbling "
               "pointer updates - sentinel head/tail nodes eliminate every null check. Ask "
               "upfront whether the standard library is allowed. Bridge to system design: the "
               "distributed version is Redis with an LRU eviction policy, plus TTLs and "
               "stampede protection.",
    "cx": "Time O(1) per operation | Space O(capacity)",
},

"time-map": {
    "name": "Time-Based Key-Value Store",
    "diff": "Medium",
    "group": "Design",
    "prompt": """set(key, value, timestamp) stores a value; get(key, timestamp) returns the
value with the largest stored timestamp <= timestamp, or "" if none.
Timestamps per key are strictly increasing.

*** Highly relevant to this role - a miniature telemetry store. ***

    s = TimeMap()
    s.set("foo","bar",1)
    s.get("foo",3)  ->  "bar" """,
    "starter": """class TimeMap:
    def __init__(self):
        pass

    def set(self, key, value, timestamp):
        pass

    def get(self, key, timestamp):
        pass
""",
    "tests": [
        ("""(lambda s: [s.set("foo","bar",1), s.get("foo",1), s.get("foo",3),
                        s.set("foo","bar2",4), s.get("foo",4), s.get("foo",5)])(TimeMap())""",
         [None, 'bar', 'bar', None, 'bar2', 'bar2']),
        ("""(lambda s: [s.set("a","x",10), s.get("a",5), s.get("a",10), s.get("b",10)])(TimeMap())""",
         [None, '', 'x', '']),
    ],
    "hint": "Timestamps arrive in increasing order, so each key's list is already sorted - "
            "binary search it. You want the rightmost entry with timestamp <= target.",
    "solution": '''from collections import defaultdict
import bisect

class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)       # key -> [(timestamp, value)]

    def set(self, key, value, timestamp):
        self.store[key].append((timestamp, value))   # already in order

    def get(self, key, timestamp):
        entries = self.store.get(key)
        if not entries:
            return ""
        # index of the first entry strictly greater than timestamp
        i = bisect.bisect_right(entries, (timestamp, chr(0x10FFFF)))
        return entries[i - 1][1] if i else ""''',
    "explain": "set is O(1) because input is already ordered; get is O(log n) via binary "
               "search. If tuple-comparison tricks feel risky under pressure, keep two parallel "
               "lists and bisect the timestamps directly. Connect it to the domain: this is how "
               "you answer 'what was this vehicle's state of charge at 3pm' against a "
               "time-series store - the real version adds partitioning by device and retention.",
    "cx": "set O(1) | get O(log n) | Space O(n)",
},

"rate-limiter": {
    "name": "Token Bucket Rate Limiter",
    "diff": "Medium",
    "group": "Design",
    "prompt": """The bucket holds up to `capacity` tokens and refills at `refill_rate` tokens
per second. allow(timestamp) spends one token and returns True, or returns
False if the bucket is empty. Timestamps are non-decreasing floats.

*** Directly job-relevant - every API gateway needs one. ***

    rl = RateLimiter(capacity=2, refill_rate=1)
    rl.allow(0) -> True ; rl.allow(0) -> True ; rl.allow(0) -> False""",
    "starter": """class RateLimiter:
    def __init__(self, capacity, refill_rate):
        pass

    def allow(self, timestamp):
        pass
""",
    "tests": [
        ("(lambda r: [r.allow(0), r.allow(0), r.allow(0), r.allow(1), r.allow(1)])(RateLimiter(2, 1))",
         [True, True, False, True, False]),
        ("(lambda r: [r.allow(0), r.allow(0), r.allow(0), r.allow(0), r.allow(1.5)])(RateLimiter(3, 2))",
         [True, True, True, False, True]),
        ("(lambda r: [r.allow(0), r.allow(100), r.allow(100)])(RateLimiter(1, 1))",
         [True, True, False]),
    ],
    "hint": "Don't run a background refill timer. Compute lazily: on each call add "
            "(elapsed x refill_rate) tokens, capped at capacity, then try to spend one.",
    "solution": '''class RateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)        # start full
        self.last_ts = 0.0

    def allow(self, timestamp):
        elapsed = timestamp - self.last_ts
        if elapsed > 0:                      # lazy refill
            self.tokens = min(self.capacity,
                              self.tokens + elapsed * self.refill_rate)
            self.last_ts = timestamp
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False''',
    "explain": "Lazy refill is the key idea - no timers, no background threads, constant time "
               "and space per client. The cap allows controlled bursts while holding the "
               "long-run average to refill_rate. Strong follow-ups to have ready: the "
               "distributed version (Redis with an atomic Lua script, since read-modify-write "
               "races across instances), per-client bucket memory cost, and how this differs "
               "from a sliding-window counter.",
    "cx": "Time O(1) | Space O(1) per client",
},
}


# ============================================================================
# HELPERS
# ============================================================================

def ensure_dir():
    os.makedirs(SOLUTIONS_DIR, exist_ok=True)


def sol_path(pid):
    return os.path.join(SOLUTIONS_DIR, pid.replace("-", "_") + ".py")


def load_progress():
    try:
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_progress(p):
    ensure_dir()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2)


def get_problem(pid):
    if pid not in PROBLEMS:
        print(f"{C.R}Unknown problem: {pid}{C.OFF}")
        print("Run  python3 gm_practice.py list  to see the available ids.")
        sys.exit(1)
    return PROBLEMS[pid]


def read_user_code(pid):
    path = sol_path(pid)
    if not os.path.exists(path):
        print(f"{C.Y}No solution file yet.{C.OFF}")
        print(f"Create one with:  {C.BOLD}python3 gm_practice.py start {pid}{C.OFF}")
        sys.exit(1)
    with open(path) as f:
        return f.read()


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_list():
    progress = load_progress()
    print(f"\n{C.BOLD}Coding Prep - Practice Problems{C.OFF}\n")
    last_group = None
    for pid, p in PROBLEMS.items():
        if p["group"] != last_group:
            last_group = p["group"]
            print(f"{C.DIM}{'-' * 62}{C.OFF}")
            print(f"{C.BOLD}{last_group}{C.OFF}")
        mark = f"{C.G}[x]{C.OFF}" if progress.get(pid) else "[ ]"
        print(f"  {mark} {pid:<24} {p['name']:<44} {C.DIM}{p['diff']}{C.OFF}")
    done = sum(1 for k in PROBLEMS if progress.get(k))
    print(f"\n{C.BOLD}{done}{C.OFF} / {len(PROBLEMS)} solved\n")


def cmd_start(pid):
    p = get_problem(pid)
    ensure_dir()
    path = sol_path(pid)
    if os.path.exists(path):
        print(f"{C.Y}File already exists:{C.OFF} {path}")
        print("Edit it, then run:  python3 gm_practice.py test " + pid)
        return
    header = f'"""\n{p["name"]}  [{p["diff"]}]\n\n{p["prompt"]}\n"""\n\n'
    with open(path, "w") as f:
        f.write(header + p["starter"])
    print(f"\n{C.BOLD}{p['name']}{C.OFF}  [{p['diff']}]\n")
    print(p["prompt"])
    print(f"\n{C.G}Created:{C.OFF} {path}")
    print(f"Open it in your editor, write your solution, then run:")
    print(f"  {C.BOLD}python3 gm_practice.py test {pid}{C.OFF}\n")


def cmd_show(pid):
    p = get_problem(pid)
    print(f"\n{C.BOLD}{p['name']}{C.OFF}  [{p['diff']}]  {C.DIM}{p['group']}{C.OFF}\n")
    print(p["prompt"] + "\n")


def cmd_test(pid):
    p = get_problem(pid)
    code = read_user_code(pid)
    ns = {}
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, sol_path(pid), "exec"), ns)
    except Exception:
        print(f"\n{C.R}Your file failed to load:{C.OFF}\n")
        traceback.print_exc(limit=2)
        return

    print(f"\n{C.BOLD}{p['name']}{C.OFF}\n")
    passed = 0
    for i, (call, expected) in enumerate(p["tests"], 1):
        try:
            with contextlib.redirect_stdout(buf):
                got = eval(call, ns)
            ok = got == expected
        except Exception as e:
            print(f"  {C.R}x{C.OFF} Case {i}: {call}")
            print(f"      {C.R}error:{C.OFF} {type(e).__name__}: {e}")
            continue
        if ok:
            passed += 1
            print(f"  {C.G}v{C.OFF} Case {i}: {call}")
        else:
            print(f"  {C.R}x{C.OFF} Case {i}: {call}")
            print(f"      expected: {expected!r}")
            print(f"      returned: {got!r}")

    total = len(p["tests"])
    print()
    if passed == total:
        print(f"  {C.G}{C.BOLD}All {total} tests passed.{C.OFF}")
        prog = load_progress()
        prog[pid] = True
        save_progress(prog)
    else:
        print(f"  {C.R}{passed} / {total} passing.{C.OFF}")
        print(f"  Stuck? Try:  {C.BOLD}python3 gm_practice.py trace {pid}{C.OFF}"
              f"   (watch your code run line by line)")
        print(f"  Or a nudge: {C.BOLD}python3 gm_practice.py hint {pid}{C.OFF}")
    print()


def cmd_trace(pid, use_solution=False, test_index=0, max_steps=400):
    """Line-by-line execution trace with live variable values."""
    p = get_problem(pid)
    code = p["solution"] if use_solution else read_user_code(pid)
    label = "the SOLUTION" if use_solution else "YOUR code"

    if test_index >= len(p["tests"]):
        print(f"{C.R}This problem only has {len(p['tests'])} test case(s).{C.OFF}")
        return
    call, expected = p["tests"][test_index]

    lines = code.split("\n")
    frames = []

    def snap(loc):
        out = {}
        for k, v in loc.items():
            if k.startswith("__"):
                continue
            try:
                if callable(v) or isinstance(v, type):
                    continue
                r = repr(v)
                out[k] = r if len(r) <= 70 else r[:67] + "..."
            except Exception:
                continue
        return out

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != "<traced>":
            return None
        if event == "line" and len(frames) < max_steps:
            frames.append((frame.f_lineno, frame.f_code.co_name, snap(frame.f_locals)))
        return tracer

    ns = {}
    buf = io.StringIO()
    err = None
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<traced>", "exec"), ns)
    except Exception as e:
        print(f"{C.R}Code failed to load: {type(e).__name__}: {e}{C.OFF}")
        return

    sys.settrace(tracer)
    try:
        with contextlib.redirect_stdout(buf):
            result = eval(call, ns)
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        result = None
    finally:
        sys.settrace(None)

    if not frames:
        print(f"{C.Y}Nothing was traced. Does your file define the function the test calls?{C.OFF}")
        return

    print(f"\n{C.BOLD}Tracing {label}{C.OFF}")
    print(f"{C.DIM}Test: {call}{C.OFF}")
    print(f"{C.DIM}{len(frames)} steps"
          f"{' (capped)' if len(frames) >= max_steps else ''}"
          f"  -  ENTER = next, b = back, q = quit, a = run all{C.OFF}\n")

    i = 0
    auto = False
    prev_vars = {}
    while i < len(frames):
        lineno, fn, vars_ = frames[i]
        os.system("clear" if os.name != "nt" else "cls")
        print(f"{C.BOLD}{p['name']}{C.OFF}  -  tracing {label}   "
              f"{C.DIM}step {i+1}/{len(frames)}{C.OFF}\n")

        # code window around the current line
        lo = max(0, lineno - 9)
        hi = min(len(lines), lineno + 8)
        for n in range(lo, hi):
            text = lines[n]
            if n + 1 == lineno:
                print(f"{C.HL}{n+1:>4} | {text:<66}{C.OFF}")
            else:
                print(f"{C.DIM}{n+1:>4} |{C.OFF} {text}")

        print(f"\n{C.BOLD}Variables{C.OFF} {C.DIM}(inside {fn}()){C.OFF}")
        if not vars_:
            print(f"  {C.DIM}(none yet){C.OFF}")
        for k, v in vars_.items():
            changed = prev_vars.get(k) != v
            marker = f"{C.Y}*{C.OFF}" if changed else " "
            colour = C.Y if changed else ""
            print(f"  {marker} {k:<14} = {colour}{v}{C.OFF}")

        print(f"\n{C.DIM}* = changed since the previous step{C.OFF}")
        prev_vars = vars_

        if auto:
            i += 1
            continue
        try:
            key = input(f"\n{C.BOLD}[enter]{C.OFF} next  |  b back  |  a all  |  q quit  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if key == "q":
            return
        elif key == "b":
            i = max(0, i - 1)
        elif key == "a":
            auto = True
            i += 1
        else:
            i += 1

    print(f"\n{C.BOLD}Finished.{C.OFF}")
    if err:
        print(f"{C.R}Execution stopped with an error: {err}{C.OFF}")
        print("The last step shown above is where it broke - that is usually the bug.")
    else:
        print(f"Returned: {result!r}")
        print(f"Expected: {expected!r}")
        print(f"{C.G}Match.{C.OFF}" if result == expected else f"{C.R}Mismatch.{C.OFF}")
    print()


def cmd_hint(pid):
    p = get_problem(pid)
    print(f"\n{C.BOLD}Hint - {p['name']}{C.OFF}\n")
    print("  " + p["hint"].replace(". ", ".\n  ") + "\n")


def cmd_solution(pid):
    p = get_problem(pid)
    print(f"\n{C.BOLD}{p['name']} - solution{C.OFF}\n")
    for line in p["solution"].split("\n"):
        print(f"  {line}")
    print(f"\n{C.BOLD}Why it works{C.OFF}\n")
    words, line = p["explain"].split(), ""
    for w in words:
        if len(line) + len(w) > 72:
            print("  " + line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        print("  " + line)
    print(f"\n  {C.DIM}{p['cx']}{C.OFF}\n")


def cmd_progress():
    prog = load_progress()
    done = [k for k in PROBLEMS if prog.get(k)]
    todo = [k for k in PROBLEMS if not prog.get(k)]
    print(f"\n{C.BOLD}Progress:{C.OFF} {C.G}{len(done)}{C.OFF} / {len(PROBLEMS)} solved\n")
    if done:
        print(f"{C.G}Solved:{C.OFF}")
        for k in done:
            print(f"  v {k:<24} {PROBLEMS[k]['name']}")
    if todo:
        print(f"\n{C.Y}Remaining:{C.OFF}")
        for k in todo:
            print(f"  . {k:<24} {PROBLEMS[k]['name']}")
    print()


def usage():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        usage()
        return
    cmd = sys.argv[1].lower()
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    flags = [a for a in sys.argv[3:]]

    if cmd in ("list", "ls"):
        cmd_list()
    elif cmd == "progress":
        cmd_progress()
    elif cmd in ("help", "-h", "--help"):
        usage()
    elif arg is None:
        print(f"{C.R}That command needs a problem id.{C.OFF}  Example: "
              f"python3 gm_practice.py {cmd} two-sum")
    elif cmd == "start":
        cmd_start(arg)
    elif cmd == "show":
        cmd_show(arg)
    elif cmd == "test":
        cmd_test(arg)
    elif cmd == "trace":
        idx = 0
        for f in flags:
            if f.startswith("--test="):
                idx = int(f.split("=")[1])
        cmd_trace(arg, use_solution=("--solution" in flags), test_index=idx)
    elif cmd == "hint":
        cmd_hint(arg)
    elif cmd in ("solution", "sol"):
        cmd_solution(arg)
    else:
        print(f"{C.R}Unknown command: {cmd}{C.OFF}\n")
        usage()


if __name__ == "__main__":
    main()
