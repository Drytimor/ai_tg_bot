def parse_mode_markdown():
    s = {
        "*": "\\*", "_": "\\_", "{": "\\{", "}": "\\}", "[": "\\[", "]": "\\]", "<": "\\<",
        ">": "\\>", "(": "\\(", ")": "\\)", "+": "\\+", "-": "\\-", ".": "\\.", "!": "\\!", "|": "\\|"
    }
    table = str.maketrans(s)
    return table

