# AI Video Prompt Pipeline (6s Veo)

Goal:
Convert SRT + audio into cinematic prompts (6 seconds each).

Constraints:

* Each prompt = exactly 6 seconds
* Prompts must be continuous (no reset)
* Maintain same character, environment, motion

Pipeline:

1. Timeline Engine

* Parse SRT
* Build continuous timeline

2. Packaging Engine (CRITICAL)

* Split timeline into fixed 6s segments (0–6, 6–12...)
* Attach relevant text to each segment

3. Context Engine

* Add context window (neighbor segments)

4. Continuity Engine

* Track:

  * previous motion
  * camera progression
  * character identity
  * environment

5. Prompt Engine

* Generate cinematic prompts:

  * must include duration: 6 seconds
  * must continue from previous motion
  * must maintain continuity

Output:
Ordered list of prompts
