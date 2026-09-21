import asyncio

from coordinator import run_group_chat, print_summary, save_output_to_file


async def main() -> None:
    feature = input(">> ")
    context = await run_group_chat(feature_requests=feature, max_turns=20)
    print_summary(context)

    out = save_output_to_file(context)

    print(f"output saved to file {out}")

if __name__ == "__main__":
    asyncio.run(main())