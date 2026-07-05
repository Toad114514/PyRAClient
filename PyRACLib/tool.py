def s2hms(total_seconds):
    if total_seconds is None:
        return "<没有足够数据>"
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"