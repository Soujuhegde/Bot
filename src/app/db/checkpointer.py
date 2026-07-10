from langgraph.checkpoint.memory import MemorySaver

# For this demo we use MemorySaver as the checkpointer per session/thread.
# To persist across restarts, this can be swapped with langgraph.checkpoint.sqlite.SqliteSaver.
checkpointer = MemorySaver()
