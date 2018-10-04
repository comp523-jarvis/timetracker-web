

def round_time_worked(time_worked, block_size=15 * 60):
    """
    Round a period of time worked to the nearest block.

    Typically this is used to round time worked to the closest 15 minute
    block.

    Args:
        time_worked:
            The time period to round, in seconds.
        block_size:
            The block size to round to, in seconds. Defaults to 15
            minutes.

    Returns:
        The time worked, in seconds, rounded to the nearest block.
    """
    time_worked += block_size / 2

    return time_worked - (time_worked % block_size)
