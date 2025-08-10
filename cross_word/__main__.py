from cross_word.cross_words import build_grid
from cross_word.utils import render_grid


def construct_parser(num_of_examples: int):
    from argparse import ArgumentParser

    parser = ArgumentParser("cross_word")
    parser.add_argument("-a", "--all", action="store_true", help="Run all the examples")
    parser.add_argument(
        "position",
        type=int,
        nargs="?",
        help=f"Run specific example. Available [1:{num_of_examples}] examples. Allowed negatives",
    )
    parser.add_argument("-p", "--phrase", nargs="?", help="Run on phrase")
    parser.add_argument(
        "-d",
        "--dry",
        action="store_true",
        help="Do not run generator, just print phrase",
    )

    def parse_args():
        args = parser.parse_args()
        provided_args = sum(
            [args.all, args.position is not None, args.phrase is not None]
        )

        if provided_args != 1:
            parser.error(
                "Exactly one of --all, position or --phrase [PHRASE] must be provided"
            )

        return args

    return parse_args


def run_on_string(phrase: str, dry: bool):
    print(f"Phrase: {phrase}")

    if not dry:
        g, _ = build_grid(phrase)
        print(render_grid(g))

    print("---")


if __name__ == "__main__":
    examples = [
        "Циферки — самое важное",
        "Я крайне разочарован",
        "Живи здесь сейчас",
        "Лови момент жизни",
        "Истина где-то между строк отчета",
        "Развлекаюсь, наблюдая за хаосом",
        "Мой сарказм — щит от реальности",
        "ааааа ббвбд гвггг зздзз",
        "Оптимизм давно вышел в отпуск",
        "Смех — мой скрытый протест",
        "Смешно? А мне нет",
        "Смешно тебе? А мне нет",
        "Смешно? Только если плакать",
        "Время лечит, но редко",
        "Смысл потерян в деталях",
        "Люди с голубыми глазами видят лучше слепых",
        "Эйнштейн не мог говорить до рождения",
        "Лошадь может дожить до конца своей жизни",
    ]

    examples_count = len(examples)
    parse = construct_parser(examples_count)
    args = parse()

    if args.phrase:
        run_on_string(args.phrase, args.dry)

    elif args.position is not None:
        error_to_raise = IndexError(
            f"Can't find example at position {args.position}. Allowed range [1:{examples_count}]"
        )
        if args.position == 0:
            raise error_to_raise

        try:
            position_delta = -1 if args.position > 0 else 0
            index = args.position + position_delta
            print(f"{(examples_count + index) % examples_count + 1}:", end=" ")
            run_on_string(examples[index], args.dry)
        except IndexError:
            raise error_to_raise

    elif args.all:
        for index, ph in enumerate(examples):
            print(f"{index+1}:", end=" ")
            run_on_string(ph, args.dry)
