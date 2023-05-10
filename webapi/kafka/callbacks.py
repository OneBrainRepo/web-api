"""
Callback functions here
Only Definitions
Implementation will be done on kafka-handler module
"""

def write_to_db_append():
    """
    Call MongoDB and append 

    chat_histories = read_by_filter_and_order("ChatHistory", order="-createdAt", author=userid)
    if not chat_histories:
        raise create_exception_404
    found_chat_history =  chat_histories[0]
    try:
        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat_history,
        push__UserQuestions=ChatHistoryAppend.UserQuestions,
        push__MachineAnswers=ChatHistoryAppend.MachineAnswers
        ) 
        # return the updated data
        if updated_chat_history is None:
            raise create_exception_500
        return {
            "status": "success",
            "message": "Conversation appended successfully.",
            "data": updated_chat_history.to_mongo().to_dict()
            }
    except:
        raise create_exception_500

    """
    pass

def write_to_db_edit_title():
    """
    try:
        found_chat = get_specific_coversation(userid=userid,chatid=ChatUpdateTitle.id)
        updated_chat_history  = update_one(
        "ChatHistory",
        found_chat,
        push__title=ChatUpdateTitle.title,
        ) 
        # return the updated data
        if updated_chat_history is None:
            raise create_exception_500
        return {
            "status": "success",
            "message": "Title has been changed successfully.",
            "data": updated_chat_history.to_mongo().to_dict()
            }
    except:
        raise create_exception_500
    """
    pass

def write_to_db_edit_message():
    """
    Write to db to edit message
    Also wait for updated answer as well
    2 way queue
    Write db to update message
    after user get a response also update the machine answer
    WILL BE IMPLEMENTED LATER
    """
    pass