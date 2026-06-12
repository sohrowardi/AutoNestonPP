import os
import re
import sys
import tkinter as tk
from tkinter import filedialog

ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"


def _supports_color() -> bool:
    """Return True when the current terminal supports ANSI color codes."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _clear_screen() -> None:
    """Clear the terminal screen to keep only one item visible at a time."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def _format_confirm_line(prefix: str, text: str, color_code: str) -> str:
    if _supports_color():
        return f"{color_code}{prefix} {text}{ANSI_RESET}"
    return f"{prefix}: {text}"


# ─────────────────────────────────────────────
#  Number-to-words helpers
# ─────────────────────────────────────────────

ONES = [
    "", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def _num_to_words(n: int) -> str:
    """Convert a non-negative integer to its spoken English form."""
    if n < 0:
        return "negative " + _num_to_words(-n)
    if n == 0:
        return "zero"
    if n < 20:
        return ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return TENS[tens] + (f"-{ONES[ones]}" if ones else "")
    if n < 1_000:
        hundreds, rest = divmod(n, 100)
        if rest == 0:
            return f"{ONES[hundreds]} hundred"
        return f"{ONES[hundreds]} hundred {_num_to_words(rest)}"
    if n < 1_000_000:
        thousands, rest = divmod(n, 1_000)
        if rest == 0:
            return f"{_num_to_words(thousands)} thousand"
        return f"{_num_to_words(thousands)} thousand {_num_to_words(rest)}"
    if n < 1_000_000_000:
        millions, rest = divmod(n, 1_000_000)
        if rest == 0:
            return f"{_num_to_words(millions)} million"
        return f"{_num_to_words(millions)} million {_num_to_words(rest)}"
    billions, rest = divmod(n, 1_000_000_000)
    if rest == 0:
        return f"{_num_to_words(billions)} billion"
    return f"{_num_to_words(billions)} billion {_num_to_words(rest)}"


def _words_to_num(text: str) -> int | None:
    """
    Convert a spoken-number string back to an integer for re-formatting.
    Handles simple cases: individual number words or short phrases.
    Returns None if parsing fails.
    """
    text = text.strip().lower()
    word_map = {}
    for i, w in enumerate(ONES):
        if w:
            word_map[w] = i
    for i, w in enumerate(TENS):
        if w:
            word_map[w] = i * 10
    word_map.update({
        "hundred": 100, "thousand": 1_000,
        "million": 1_000_000, "billion": 1_000_000_000,
    })

    tokens = re.split(r"[\s\-]+", text)
    total = 0
    current = 0
    try:
        for token in tokens:
            if token not in word_map:
                return None
            val = word_map[token]
            if val == 100:
                current *= 100
            elif val >= 1_000:
                total += (current if current else 1) * val
                current = 0
            else:
                current += val
        return total + current
    except Exception:
        return None


def _comma_int(n: int) -> str:
    """Format an integer with commas: 40000 → '40,000'."""
    return f"{n:,}"


# ─────────────────────────────────────────────
#  Confirmation prompt
# ─────────────────────────────────────────────

def _edit_line_popup(prompt_text: str, default: str) -> str | None:
    """Open a Tkinter popup editor prefilled with the suggested line."""
    root = tk.Tk()
    root.withdraw()
    top = tk.Toplevel(root)
    top.title("Edit suggested line")

    # Size the popup based on the content length, with reasonable limits.
    min_width = 500
    max_width = 1200
    estimated_width = int(max(40, min(len(default), 140)) * 8 + 120)
    width_pixels = min(max(min_width, estimated_width), max_width)
    height_pixels = 140

    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x = max(0, (screen_width - width_pixels) // 2)
    y = max(0, (screen_height - height_pixels) // 2)
    top.geometry(f"{width_pixels}x{height_pixels}+{x}+{y}")
    top.minsize(min_width, height_pixels)
    top.resizable(True, False)

    def close(result: str | None) -> None:
        top.result = result
        top.destroy()

    def on_escape(event=None):
        close(None)

    def on_enter(event=None):
        close(entry.get())
        return "break"

    label = tk.Label(top, text=prompt_text, anchor="w")
    label.pack(fill="x", padx=12, pady=(12, 6))

    frame = tk.Frame(top)
    frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    scrollbar = tk.Scrollbar(frame, orient="horizontal")
    entry = tk.Entry(frame, font=("Segoe UI", 11), width=1)
    entry.insert(0, default)
    entry.grid(row=0, column=0, sticky="nsew")
    scrollbar.config(command=entry.xview)
    entry.configure(xscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=0, sticky="ew")

    frame.columnconfigure(0, weight=1)

    button_frame = tk.Frame(top)
    button_frame.pack(fill="x", padx=12, pady=(0, 12))
    ok_button = tk.Button(button_frame, text="Save", command=lambda: close(entry.get()))
    cancel_button = tk.Button(button_frame, text="Cancel", command=lambda: close(None))
    ok_button.pack(side="right", padx=(0, 6))
    cancel_button.pack(side="right")

    top.bind("<Escape>", on_escape)
    top.bind("<Return>", on_enter)
    top.protocol("WM_DELETE_WINDOW", on_escape)

    top.update_idletasks()
    top.lift()
    top.attributes("-topmost", True)
    top.focus_force()
    entry.focus_force()
    entry.selection_range(0, tk.END)
    entry.icursor(tk.END)
    top.grab_set()
    top.after(50, lambda: top.attributes("-topmost", False))
    top.wait_window()
    root.destroy()
    return getattr(top, "result", None)


def _get_single_key(prompt: str) -> str:
    try:
        import msvcrt
        sys.stdout.write(prompt)
        sys.stdout.flush()
        ch = msvcrt.getwch()
        if ch == "\r":
            ch = "\n"
        sys.stdout.write("\n")
        return ch
    except ImportError:
        try:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
        except (ImportError, OSError, AttributeError):
            return input(prompt)[:1]
        try:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            sys.stdout.write("\n")
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _confirm(original: str, proposed: str) -> str | None:
    """Ask the user to accept, reject, or manually correct the full proposed line."""
    _clear_screen()
    print(_format_confirm_line("🔴", original, ANSI_RED))
    print(_format_confirm_line("🟢", proposed, ANSI_GREEN))
    choice = _get_single_key(
        "\nPress Enter to accept, n to reject, or Space to edit: ",
    )
    if choice in ("\n", "\r"):
        return proposed
    if choice.lower() == "n":
        return None
    if choice == " ":
        edited = _edit_line_popup("Edit the suggested line:", proposed)
        return proposed if edited is None else edited
    return proposed


# ─────────────────────────────────────────────
#  Step 1 – Line cleanup & normalisation
# ─────────────────────────────────────────────

# Characters that are illegal in Windows / macOS / Linux filenames
_INVALID_CHARS = r'?\\/:*"<>|'
_INVALID_RE    = re.compile(r'[' + re.escape(_INVALID_CHARS) + r']')

# Matches a trailing single period that is NOT part of an ellipsis
_TRAILING_PERIOD_RE = re.compile(r'(?<!\.)\.(?!\.)$')


def clean_line(line: str) -> str:
    """Apply the deterministic cleanup pipeline to a single line."""
    # 1. Strip leading/trailing whitespace first so prefix check is reliable
    text = line.strip()

    # 2. Remove "- " prefix
    if text.startswith("- "):
        text = text[2:]

    # 3. Remove single trailing period (but NOT ellipsis)
    text = _TRAILING_PERIOD_RE.sub("", text)

    # 4. Strip whitespace again in case the period removal left a space
    text = text.strip()

    # 5. Remove invalid filename characters
    text = _INVALID_RE.sub("", text)

    return text


# ─────────────────────────────────────────────
#  Step 2 – Interactive number processing
# ─────────────────────────────────────────────

# Repetition marker – must be preserved: x2, x3, …
_REPEAT_RE = re.compile(r'\bx\d+\b', re.IGNORECASE)

# Currency context words
_CURRENCY_CONTEXT_RE = re.compile(
    r'\b(?:dollar|dollars|buck|bucks|cash|usd|cent|cents)\b',
    re.IGNORECASE,
)

# Spoken number words (single tokens or short compound phrases)
_NUMBER_WORD_RE = re.compile(
    r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|'
    r'thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|'
    r'thirty|forty|fifty|sixty|seventy|eighty|ninety|'
    r'hundred|thousand|million|billion)'
    r'(?:[\s\-](?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|'
    r'thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|'
    r'thirty|forty|fifty|sixty|seventy|eighty|ninety|'
    r'hundred|thousand|million|billion))*\b',
    re.IGNORECASE,
)

# Raw digit sequences (not already inside [brackets])
_DIGIT_RE = re.compile(r'(?<!\[)\b(\d[\d,]*)\b(?!\])')


def _protect_repetitions(text: str):
    """
    Replace xN markers with placeholders so they are never touched by
    number-processing regexes.  Returns (protected_text, restore_map).
    """
    placeholders = {}
    def _rep(m):
        key = f"\x00REPEAT{len(placeholders)}\x00"
        placeholders[key] = m.group(0)
        return key
    return _REPEAT_RE.sub(_rep, text), placeholders


def _restore_repetitions(text: str, placeholders: dict) -> str:
    for key, val in placeholders.items():
        text = text.replace(key, val)
    return text


_UNIT_AFTER_MONEY_RE = re.compile(
    r'^\s*(?:million|billion|thousand|hundred|a\s+(?:month|week|year|day|hour|minute|second)|per\s+(?:month|week|year|day|hour|minute|second))\b',
    re.IGNORECASE,
)

_LEADING_BRACKET_RE = re.compile(r'^(\[[^\]]+\])\s*(.*)$')
_DOLLAR_AMOUNT_RE = re.compile(r'\$([0-9][0-9,]*)')
# Full dollar + optional scale (e.g. "$750 million")
_DOLLAR_FULL_RE = re.compile(r'\$\s*([0-9][0-9,]*)(?:\s*(million|thousand|billion|hundred))?', re.IGNORECASE)

# Digits with optional scale (e.g. "43 million")
_DIGIT_FULL_RE = re.compile(r'(?<!\[)\b([0-9][0-9,]*)(?:\s*(million|thousand|billion|hundred))\b(?!\])', re.IGNORECASE)


def _has_currency_context(text: str) -> bool:
    return bool(_CURRENCY_CONTEXT_RE.search(text) or "$" in text)


def _normalize_leading_bracket(prefix: str, remainder: str) -> str:
    if prefix.startswith("[$") and not _has_currency_context(remainder):
        return "[" + prefix[2:]
    return prefix


def _capitalize_first_letter(text: str) -> str:
    return re.sub(r'([A-Za-z])', lambda m: m.group(1).upper(), text, count=1)


def _split_leading_bracket(line: str) -> tuple[str, str]:
    match = _LEADING_BRACKET_RE.match(line)
    if not match:
        return "", line
    return match.group(1), match.group(2)


def _currency_to_words(value: int, short_form: bool = False) -> str:
    if short_form and 100 < value < 1_000:
        hundreds, rest = divmod(value, 100)
        if rest == 0:
            return f"{ONES[hundreds]} hundred"
        return f"{ONES[hundreds]} {_num_to_words(rest)}"
    return _num_to_words(value)


def _format_leading_amount_line(text: str) -> str | None:
    stripped = text.strip()
    money = re.fullmatch(r'\$([0-9][0-9,]*)', stripped)
    if money:
        raw = money.group(1)
        value = int(raw.replace(",", ""))
        words = _currency_to_words(value)
        unit = _money_unit(value)
        return f"[${raw}] {_capitalize_first_letter(words + ' ' + unit)}"
    digits = re.fullmatch(r'([0-9][0-9,]*)', stripped)
    if digits:
        raw = digits.group(1)
        value = int(raw.replace(",", ""))
        words = _num_to_words(value)
        return f"[{raw}] {_capitalize_first_letter(words)}"
    return None


def _money_unit(value: int, explicit: str | None = None) -> str:
    if explicit:
        explicit = explicit.lower()
        if explicit.startswith('doll'):
            return 'dollar' if value == 1 else 'dollars'
        if explicit.startswith('buck'):
            return 'buck' if value == 1 else 'bucks'
        return explicit
    return 'dollar' if value == 1 else 'dollars'


def _replace_dollar_amount(m: re.Match, text: str) -> str:
    raw = m.group(1)
    value = int(raw.replace(",", ""))
    after = text[m.end():]
    omit_dollars = bool(_UNIT_AFTER_MONEY_RE.match(after))
    words = _currency_to_words(value, short_form=(value < 1_000 and omit_dollars))
    if omit_dollars:
        return words
    return f"{words} {_money_unit(value)}"


def _replace_bare_digits(m: re.Match) -> str:
    raw = m.group(1)
    return _num_to_words(int(raw.replace(",", "")))


def _apply_number_conversion(text: str, allow_leading_bracket: bool) -> str:
    if allow_leading_bracket:
        leading = _format_leading_amount_line(text)
        if leading is not None:
            return leading

    converted = _DOLLAR_AMOUNT_RE.sub(lambda m: _replace_dollar_amount(m, text), text)
    converted = _DIGIT_RE.sub(_replace_bare_digits, converted)
    return converted


# New authoritative reference-generation pipeline
def remove_leading_reference(text: str) -> tuple[str, str]:
    """Strip an existing leading bracketed reference and return (ref, remainder).
    If none present, returns ("", text).
    """
    m = re.match(r'^\s*\[([^\]]+)\]\s*(.*)$', text)
    if not m:
        return "", text
    return m.group(1), m.group(2)


def find_primary_number(text: str) -> tuple[int | None, bool, re.Match | None]:
    """Find the primary numeric value in text.
    Returns (value, is_money, match) where match is the regex match that located the number (if any).
    Search order: explicit $ amounts, bare digits, spoken-number phrases.
    """
    scale_factors = {
        'hundred': 100,
        'thousand': 1_000,
        'million': 1_000_000,
        'billion': 1_000_000_000,
    }

    # 1) Full $amount with optional scale (captures $750 million)
    m = _DOLLAR_FULL_RE.search(text)
    if m:
        raw = m.group(1)
        scale = m.group(2)
        try:
            base = int(raw.replace(",", ""))
            if scale:
                factor = scale_factors.get(scale.lower(), 1)
                value = base * factor
            else:
                value = base
            return value, True, m
        except ValueError:
            pass

    # 2) Digits with explicit scale (e.g. "43 million")
    m = _DIGIT_FULL_RE.search(text)
    if m:
        raw = m.group(1)
        scale = m.group(2)
        try:
            base = int(raw.replace(",", ""))
            factor = scale_factors.get(scale.lower(), 1) if scale else 1
            value = base * factor
            # classify as money if currency word follows the match
            after = text[m.end():]
            is_money = bool(_CURRENCY_CONTEXT_RE.search(after))
            return value, is_money, m
        except ValueError:
            pass

    # 3) Bare digits (may be monetary if currency nearby)
    m = _DIGIT_RE.search(text)
    if m:
        raw = m.group(1)
        try:
            value = int(raw.replace(",", ""))
            after = text[m.end():]
            is_money = bool(_CURRENCY_CONTEXT_RE.search(after)) or bool(re.search(r'\$', text[:m.start()]))
            return value, is_money, m
        except ValueError:
            pass

    # 4) Spoken number phrases (may include scale words)
    m = _NUMBER_WORD_RE.search(text)
    if m:
        words = m.group(0)
        parsed = _words_to_num(words)
        if parsed is not None:
            after = text[m.end():]
            is_money = bool(_CURRENCY_CONTEXT_RE.search(after)) or ('$' in text[:m.start()])
            return parsed, is_money, m

    return None, False, None


def generate_reference(value: int, is_money: bool) -> str:
    if is_money:
        return f"[${_comma_int(value)}]"
    return f"[{_comma_int(value)}]"


def _replace_primary_number_with_words(text: str, match: re.Match, value: int, is_money: bool) -> str:
    """Replace the matched numeric token with its normalized spoken form.
    For money, preserve following unit words (dollars/bucks) and handle singular/plural.
    """
    start, end = match.span()
    before = text[:start]
    after = text[end:]

    # Determine if the numeric occurrence is followed by a currency word
    after_strip = after.lstrip()
    currency_match = re.match(r'^(dollars|dollar|bucks|buck)\b', after_strip, re.IGNORECASE)

    words = _num_to_words(value)
    if is_money:
        # choose unit to append
        if currency_match:
            replacement = words + ' ' + _money_unit(value, currency_match.group(1))
            # Avoid duplicating the same currency unit if it is already present after the match.
            after = re.sub(
                r'^\s*' + re.escape(currency_match.group(0)) + r'\b',
                '',
                after,
                flags=re.IGNORECASE,
            )
        else:
            # No explicit unit word after numeric – use singular/plural correctly
            replacement = words + ' ' + _money_unit(value)
    else:
        replacement = words

    # preserve spacing: if there was no space between number and following punctuation, keep it
    return before + replacement + after


def normalize_sentence_from_content(text: str, primary_match: re.Match | None, value: int | None, is_money: bool) -> str:
    """Normalize sentence contents to spoken words for the primary numeric token and to a consistent case.
    Leave other tokens mostly alone, but convert remaining bare digits and $amounts to words as well.
    """
    # First replace primary occurrence (if any) with words
    result = text
    if value is not None and primary_match is not None:
        result = _replace_primary_number_with_words(result, primary_match, value, is_money)

    # Then replace any remaining $amounts and bare digits
    result = _DOLLAR_AMOUNT_RE.sub(lambda m: _replace_dollar_amount(m, result), result)
    result = _DIGIT_RE.sub(_replace_bare_digits, result)

    # Normalize spacing and capitalization: sentence authoritative but make sentence lowercase except first letter
    result = result.strip()
    if result:
        result = result[0].upper() + result[1:]
    return result


def process_line(line: str) -> str:
    """Authoritative processing for a single line producing a standardized reference + sentence.
    Preserves repetition markers, asks confirmation if a change is proposed.
    """
    # Strip version suffixes like " (0)" before processing; we'll reattach via assign_version
    line_no_version = re.sub(r'\s*\(\d+\)\s*$', '', line)
    text, placeholders = _protect_repetitions(line_no_version)

    # remove any existing leading bracketed reference
    _existing_ref, remainder = remove_leading_reference(text)

    # find primary numeric value from content
    value, is_money, match = find_primary_number(remainder)

    if value is None:
        # No numeric content: if there was an existing leading reference, normalize it; otherwise return unchanged
        restored_remainder = _restore_repetitions(remainder, placeholders)
        if _existing_ref:
            # try to parse existing ref as numeric (allow leading $)
            ref_text = _existing_ref.strip()
            is_money_ref = False
            if ref_text.startswith("$"):
                is_money_ref = True
                ref_text = ref_text[1:]
            try:
                ref_val = int(ref_text.replace(",", ""))
                new_ref = generate_reference(ref_val, is_money_ref)
                return f"{new_ref} {restored_remainder}" if restored_remainder else new_ref
            except Exception:
                # not a numeric ref - just reattach original normalized bracket
                return f"[{_existing_ref}] {restored_remainder}" if restored_remainder else f"[{_existing_ref}]"
        return restored_remainder

    # generate new reference from authoritative content
    reference = generate_reference(value, is_money)

    # normalize sentence content (convert numbers to words etc.)
    normalized = normalize_sentence_from_content(remainder, match, value, is_money)

    proposed = f"{reference} {normalized}"
    proposed = _restore_repetitions(proposed, placeholders)

    if proposed != line:
        correction = _confirm(line, proposed)
        if correction is None:
            return line
        return correction
    return line


# ─────────────────────────────────────────────
#  Version-counter database helpers
# ─────────────────────────────────────────────

def load_sentence_counts(a_file_path: str) -> dict[str, list[int]]:
    """Read the Clip Collections database into a sentence → [numbers] map."""
    sentence_count: dict[str, list[int]] = {}
    with open(a_file_path, 'r', encoding='utf-8') as fh:
        for line in fh:
            try:
                sentence, number = line.rsplit(' ', 1)
                number = int(number.strip('()\n'))
                sentence_count.setdefault(sentence, []).append(number)
            except ValueError:
                print(f"Skipping invalid line in database: {line.strip()}")
    return sentence_count


def assign_version(sentence: str, sentence_count: dict[str, list[int]]) -> str:
    """Return 'sentence (N)' where N is one higher than the current max."""
    if sentence in sentence_count:
        next_number = max(sentence_count[sentence]) + 1
    else:
        next_number = 0
    sentence_count.setdefault(sentence, []).append(next_number)
    return f"{sentence} ({next_number})"


# ─────────────────────────────────────────────
#  Output-file naming
# ─────────────────────────────────────────────

def versioned_output_path(b_file_path: str) -> str:
    """
    Given /path/to/scene.txt, return /path/to/scene_1.txt (or _2, _3 …)
    such that no existing file is overwritten.
    """
    base_dir  = os.path.dirname(b_file_path)
    base_name = os.path.splitext(os.path.basename(b_file_path))[0]

    # Strip any existing _N suffix so we always start counting from 1
    base_name = re.sub(r'_\d+$', '', base_name)

    counter = 1
    while True:
        candidate = os.path.join(base_dir, f"{base_name}_{counter}.txt")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


# ─────────────────────────────────────────────
#  Core pipeline
# ─────────────────────────────────────────────

def process_files(a_file_path: str, b_file_path: str) -> str:
    """
    Run the full pipeline:
      1. Load the Clip Collections database.
      2. For each line in the input file:
         a. Clean & normalise.
         b. Interactively process numbers.
         c. Assign a version counter from the database.
      3. Write output to a new versioned file.
    Returns the output file path.
    """
    sentence_count = load_sentence_counts(a_file_path)

    output_lines: list[str] = []
    with open(b_file_path, 'r', encoding='utf-8') as fh:
        raw_lines = fh.readlines()

    for raw_line in raw_lines:
        # Step 1 – deterministic cleanup
        cleaned = clean_line(raw_line)

        # Step 2 – authoritative reference & number processing
        processed = process_line(cleaned)

        # Step 3 – version assignment
        versioned = assign_version(processed, sentence_count)

        output_lines.append(versioned + "\n")

    output_path = versioned_output_path(b_file_path)
    with open(output_path, 'w', encoding='utf-8') as fh:
        fh.writelines(output_lines)

    return output_path


# ─────────────────────────────────────────────
#  File selection helpers
# ─────────────────────────────────────────────

def select_file(title: str, initial_dir: str = "", filetypes: tuple[tuple[str, str], ...] = (("Text files", "*.txt"),)) -> str:
    if not initial_dir:
        initial_dir = os.getcwd()
    if not os.path.isdir(initial_dir):
        initial_dir = os.getcwd()
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title=title,
        initialdir=initial_dir,
        filetypes=filetypes,
        defaultextension=".txt",
    )
    root.destroy()
    return file_path


def find_file(folder: str, prefix: str = "", suffix: str = ".txt",
              exclude_prefix: str = "") -> list[str]:
    results = []
    for name in os.listdir(folder):
        if not name.endswith(suffix):
            continue
        if prefix and not name.startswith(prefix):
            continue
        if exclude_prefix and name.startswith(exclude_prefix):
            continue
        results.append(os.path.join(folder, name))
    return results


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))

    # ── Locate the Clip Collections database ──────────────────────────────
    clip_files = find_file(folder, prefix="Clip Collections")
    if clip_files:
        a_file_path = clip_files[0]
        print(f"Database file found: {os.path.basename(a_file_path)}")
    else:
        print("No 'Clip Collections' file found. Please select the database file.")
        a_file_path = select_file(
            "Select the main database file (with numbers)",
            folder,
            (("Text files", "*.txt"),),
        )

    # ── Locate the target text file ────────────────────────────────────────
    txt_files = find_file(folder, suffix=".txt", exclude_prefix="Clip Collections")
    if len(txt_files) == 1:
        b_file_path = txt_files[0]
        print(f"Target file found:   {os.path.basename(b_file_path)}")
    elif len(txt_files) > 1:
        print("Multiple target files found. Please select the file to process.")
        b_file_path = select_file(
            "Select the file to be processed",
            folder,
            (("Text files", "*.txt"),),
        )
    else:
        print("Error: No target file found.")
        b_file_path = ""

    # ── Validate and run ───────────────────────────────────────────────────
    errors = []
    if not a_file_path:
        errors.append("No database file selected.")
    elif not os.path.isfile(a_file_path):
        errors.append(f"Database file not found: '{a_file_path}'")
    if not b_file_path:
        errors.append("No target file selected.")
    elif not os.path.isfile(b_file_path):
        errors.append(f"Target file not found: '{b_file_path}'")

    if errors:
        for e in errors:
            print(f"Error: {e}")
    else:
        output_path = process_files(a_file_path, b_file_path)
        print(f"\nDone. Output written to: '{output_path}'")

    input("\nPress Enter to exit…")
