"""A pipeline state list record with variant 0 and no answers or questions stands for the variant nothing bound makes.

Lists converted from records that hold no texture answers (assets/pipeline_states/contrib/*-fritchii-recipe*) name a program
variant by nothing: variant 0, no answers, no questions. state_list_prepare (gpu/vk/vk_draw.cpp) prepares those with the
variant the program's translation makes with nothing bound (seed_plain_of, gpu/vk/vk_shader.cpp), the one draws whose textures
are what the instructions declare ask for. Not with seed_variant_of and empty answers: that variant would have no answers, and
a variant without answers stands for any textures (still_valid). And only when the record's own variant is not found: a program
without textures has variant 0 already. This checks the source.
python -I -B tests/test_state_list_plain.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def body(text, marker):
    start = text.index(marker)
    at = text.index("{", start) + 1
    depth = 1
    while depth:
        depth += (text[at] == "{") - (text[at] == "}")
        at += 1
    return text[start:at]


def main():
    shader = (ROOT / "gpu" / "vk" / "vk_shader.cpp").read_text(encoding="utf-8")
    made = body(shader, "static const Program* seed_variant_made(")
    plain = body(shader, "const Program* seed_plain_of(")
    of = body(shader, "const Program* seed_variant_of(")
    if "if (questions) questions_in = questions" not in made:
        raise SystemExit("seed_variant_made gives the translation questions even when none are given: the plain variant would "
                         "not answer them as nothing bound does")
    if "nullptr, nullptr" not in plain:
        raise SystemExit("seed_plain_of does not translate with nothing given")
    if "&questions, &answers" not in of:
        raise SystemExit("seed_variant_of does not hand its questions and answers to seed_variant_made")
    draw = (ROOT / "gpu" / "vk" / "vk_draw.cpp").read_text(encoding="utf-8")
    prep = body(draw, "void state_list_prepare(")
    if "!r.variant && !r.nanswers && !r.nquestions" not in prep:
        raise SystemExit("state_list_prepare does not tell records with variant 0 and no answers or questions apart")
    if "seed_plain_of(" not in prep:
        raise SystemExit("state_list_prepare does not make the variant nothing bound makes for those records")
    found = prep.index("const Program* p = program_find_portable(key, r.variant);", prep.index("plain_of.emplace"))
    if prep.index("if (!p && plain(r))", found) - found > 120:
        raise SystemExit("state_list_prepare takes the variant nothing bound makes before the record's own variant")
    print("PASS: records without a variant are prepared with the variant nothing bound makes, after their own")


if __name__ == "__main__":
    main()
