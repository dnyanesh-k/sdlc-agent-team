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

    context = GroupChatContext(feature_requests=feature_request, max_turns=max_turns)
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

def print_summary(context: GroupChatContext) -> None:
    print(f"\n{'=' * 60}")
    print(f"  SPRINT SUMMARY")
    print(f"\n{'=' * 60}")
    print(f"Feature:  {context.feature_requests}")
    print(f"Phase:    {context.current_phase}")
    print(f"Turns:    {context.turn_count}")
    print(f"Tests OK: {context.all_tests_passed}")

    if context.requirements:
        print("\n Requirements:")
        for r in context.requirements:
            print(f"  - [{r.id}] {r.title} : {r.description[:80]}")

    if context.code.files:
        print(f"\n Code Files:")
        for fname in context.code.files:
            print(f"    -{fname}")

    if context.test_result:
        print("\n Test Results:")
        for tr in context.test_result:
            status = "PASS" if tr.passed else "FAIL"
            print(f"    - {tr.test_file} : {status}")

    print(f"\n {'=' * 60}\n")


def save_output_to_file(context: GroupChatContext, filename: str ="sprint_output.md") -> str:
    lines = [
        '#Sprint Output\n',
        f"## Feature: {context.feature_requests}",
        f"**Phase:** {context.current_phase}",
        f"**Turns:** {context.turn_count}",
        f"**Tests Passed:** {context.all_tests_passed}"
    ]

    if context.requirements:
        lines.append("##Requirements:\n")
        for r in context.requirements:
            lines.append(f"- **[{r.id}] {r.title}**: {r.description}")
            for ac in r.acceptance_criteria:
                lines.append(f"  - {ac}")
        lines.append("")

    if context.code.files:
        lines.append("##Code:\n")
        for fname, content in context.code.files.items():
            lines.append(f"### {fname}\n")
            lines.append(f"```python\n{content}\n```\n")

    if context.test_result:
        lines.append("## Test Results\n")
        for tr in context.test_result:
            status = "PASS" if tr.passed else "FAIL"
            lines.append(f"- **{tr.test_file}**: {status} ({tr.total_tests} tests, {tr.failure} failures, {tr.errors} erros)")
        lines.append("")

    lines.append("## Conversation Log\n")
    for entry in context.conversation_log:
        lines.append(f"### Turn {entry['turn']} - {entry['speaker']}\n")
        lines.append(f"{entry['message']}\n")

    content = "\n".join(lines)
    with open(filename, 'w') as f:
        f.write(content)

    return filename









