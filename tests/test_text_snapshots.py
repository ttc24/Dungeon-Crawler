from dungeoncrawler import main, map_text


def test_intro_text_snapshot(file_regression):
    text = main.get_intro_text()
    file_regression.check(text, extension=".txt")


def test_map_legend_snapshot(file_regression):
    text = map_text.get_legend_text()
    file_regression.check(text, extension=".txt")
