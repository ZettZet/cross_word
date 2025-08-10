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
        # FIXME Горизонтальные слова слипаются с вертикальными
        # Ожидаемо
        # Ж    З
        # И    Д
        # В  С Е Й Ч А С
        # И    С
        #      Ь
        "Живи здесь сейчас",
        "Лови момент жизни",
        "Истина где-то между строк отчета",
        "Развлекаюсь, наблюдая за хаосом",
        # FIXME Новое горизонтальное слово не должно сильно отдалять вертикальное (МОЙ стоит в конце САРКАЗМ, хотя идет раньше в предложении)
        # FIXME Нельзя объединять два вертикальных слова через горизонтально, состоящее из 2 букв (ОТ получилось из 7-й буквы РЕАЛЬНОСТИ и 3-й буквы ЩИТ)
        # NOTE Новое правило: по визуальному весу каждое следующее слово должно находиться правее и ниже предыдущего
        # То есть оно может выглядывать слева от вертикального, но хотя бы половина должна находиться справа от вертикального
        "Мой сарказм — щит от реальности",
        # FIXME При работе с каждым словом нужно пытаться поставить его не только в сравнении с предыдущим, но со всеми предыдущими вплоть до первого вертикального
        # Ожидаемое:
        # А      Б
        # А      Б
        # А    Г В Г Г Г
        # А      Б
        # А  З З Д З З
        "ааааа ббвбд гвггг зздзз",
        # NOTE В этом примере явно видно неправильное поведение
        # Д А В Н О   О
        #     Ы   П   Т
        #     Ш   Т   П
        #     Е   И   У
        #     Л   М   С
        #         И   К
        #         З
        #         М
        # ДАВНО и ВЫШЕЛ стоят вообще целиком перед первым словом (ОПТИМИЗМ)
        # Ожидаемое:
        # О  Д             О
        # П  А             Т
        # Т  В Ы Ш Е Л  В  П
        # И  Н             У
        # М  О             С
        # И                К
        # З
        # М
        "Оптимизм давно вышел в отпуск",
        "Смех — мой скрытый протест",
        # TODO Расставлять потерянные знаки препинания
        # Ожидаемое:
        # С        Т
        # М        О
        # Е    Е С Л И
        # Ш        Ь
        # Н  П Л А К А Т Ь
        # О        О
        # ?
        "Смешно? А мне нет",
        "Смешно тебе? А мне нет",
        "Смешно? Только если плакать",
        # Ожидаемое:
        #   В        Н Р
        #   Р        О Е
        # Л Е Ч И Т    Д
        #   М          К
        #   Я          О
        "Время лечит, но редко",
        "Смысл потерян в деталях",
        # Ожидаемое:
        #                     В
        # Л   С   Г Л А З А М И  С Л Е П Ы Х
        # Ю       О           Д    У
        # Д       Л           Я    Ч
        # И       У           Т    Ш
        #         Б                Е
        #         Ы
        #         М
        #         И
        "Люди с голубыми глазами видят лучше слепых",
        "Эйнштейн не мог говорить до рождения",
        # Ожидаемое:
        #
        #   Л        Д О       К
        # М О Ж Е Т  О     С В О Е Й
        #   Ш        Ж   Ж И З Н И
        #   А        И         Ц
        #   Д        Т         А
        #   Ь        Ь
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
