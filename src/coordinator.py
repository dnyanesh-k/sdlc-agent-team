from agents import Agent, RunConfig, trace, Runner

from models import GroupChatContext, SpeakerRole
from team_agents import developer, product_manager
from models import SprintPhase

SPEAKER_MAP : dict [SpeakerRole, Agent] = {
    SpeakerRole.PRODUCT_MANAGER: product_manager,
    SpeakerRole.DEVELOPER: developer,
}

TURN_ORDER = [
    SpeakerRole.PRODUCT_MANAGER,
    SpeakerRole.DEVELOPER,
]

def _print_turn(speaker: SpeakerRole, message: str, turn: int) -> None:
    print(f"\n[Turn {turn}] {speaker.value}")
    print("--" * 25)
    for line in message.split("\n"):
        print(f" {line}")

def _detect_termination(output: str) -> bool:
    for line in reversed(output.strip().split("\n")):
        stripped = line.strip()
        if stripped.upper() == "TERMINATE":
            return True
        if stripped:
            return False
    return False


def _advance_phase(context: GroupChatContext) -> None:
    if context.current_phase == SprintPhase.REQUIREMENTS and context.requirements:
        context.current_phase = SprintPhase.IMPLEMENTATION
    elif context.current_phase == SprintPhase.IMPLEMENTATION:
        context.current_phase = SprintPhase.TESTING
    elif context.current_phase == SprintPhase.TESTING:
        context.current_phase = SprintPhase.DONE


async def run_group_chat(
    feature_request: str,
    max_turns: int = 24,
)-> GroupChatContext:
    print(f"\n{"=" * 60}")
    print(" Collaborative Software Engineering Chat")
    print(f"\n{"=" * 60}")
    print(f"Feature Request : {feature_request}\n")

    context = GroupChatContext(feature_requests=feature_request, maxt_turns=max_turns)
    current_speaker = SpeakerRole.PRODUCT_MANAGER
    run_config = RunConfig(workflow_name="GroupChat")

    with trace("GroupChat"):
        for turn in range(1, max_turns + 1):
            context.turn_count = turn
            agent = SPEAKER_MAP[current_speaker]

            if not context.conversation_log:
                user_input = (
                    f"Feature request : {feature_request}\n\n"
                    "Define requirements for this feature."
                )
            else:
                last_msg = context.conversation_log[-1]["message"]
                user_input = (
                    f"[Turn {turn} -- {current_speaker.value}]\n\n"
                    f"Previous Message: \n{last_msg}\n\n"
                    "Continue the discussion. Respond in you role."
                )

            print(f"{current_speaker.value} is thinking.")
            try:
                result = await Runner.run(
                    starting_agent=agent,
                    input=user_input,
                    context=context,
                    max_turns=20,
                    run_config=run_config
                )
            except Exception as e:
                print(f"\n Agent Error {e}")
                break

            output = str(result.final_output) if result.final_output else "(no output)"
            context.log(current_speaker, output)
            _print_turn(current_speaker, output, turn)
            
            if _detect_termination(output):
                print(f"=" * 60)
                print(f"  Terminate received. Sprint done in {turn} turns.")
                print(f"{'=' * 60}\n")
                context.terminate = True
                context.current_phase = SprintPhase.DONE
                break

            _advance_phase(context)

            idx = (TURN_ORDER.index(current_speaker) + 1) % len(TURN_ORDER)
            current_speaker = TURN_ORDER[idx]

        else:
            print(f"\n Max Turns {max_turns} reached. Stopping.\n")
            context.terminate = True

    return context










