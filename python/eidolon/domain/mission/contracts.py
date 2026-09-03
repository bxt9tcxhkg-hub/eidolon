from typing import Literal

AgentRunState = Literal[
    'understanding',
    'planning',
    'spawning_work',
    'acting',
    'waiting',
    'blocked',
    'verifying',
    'completed',
    'failed',
    'cancelled',
]

AgentRunPhase = Literal['understand', 'plan', 'execute', 'verify', 'finalize']
