from agent.agent_loop import run_agent

if __name__ == "__main__":
    q = input("Question: ")
    print("\nThinking...\n")
    print("Answer:", run_agent(q))
