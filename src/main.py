import asyncio

async def main()-> None:
    feature = input(">> ")
    context = await run_group_chat(feature_request = feature, max_turns = 20)
    print_summary(context)

    out = save_output_to_file(context)

    print(f"output saved to file {out}")

if __name__ == "__main__":
    asyncio.run(main(0))