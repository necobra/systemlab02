"""
<COMMAND> :=       Побудувати <TYPE_TRIANGLE> <FIGURE> |
                   Провести <ELEMENT> в трикутнику <TRIANGLE>

<ELEMENT> :=       медіана|бісектриса|висота <POINT><POINT>

<POINT> :=         [A-Z]

<FIGURE> :=        <TRIANGLE>

<TRIANGLE> :=      <POINT><POINT><POINT>

<TYPE_TRIANGLE> := (<TYPE_ANGLE><TYPE_SIDE>) | рівносторонній
<TYPE_SIDE> :=     довільний|рівнобедрений
<TYPE_ANGLE> :=    гострокутний|прямокутний|тупокутний

<DOT> (розділяє команди)
"""


import re

from draw import DiagramDrawer


class Node:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children else []

    def __repr__(self, level=0):
        ret = "\t" * level + f"{self.type}: {self.value}\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

class Parser:
    TOKENS = [
        ("COMMAND", r"(?i)\bпобудувати\b|\bпровести\b|\bвідмітити\b"),
        ("FIGURE", r"(?i)\bтрикутник(a|у)?\b"),
        ("TYPE_ANGLE", r"(?i)\bгострокутний\b|\bпрямокутний\b|\bтупокутний\b"),
        ("TYPE_SIDE", r"(?i)\bдовільний\b|\bрівнобедрений\b"),
        ("TYPE_TRIANGLE", r"(?i)\bрівносторонній\b"),
        ("ELEMENT", r"(?i)\bмедіан(а|у|и|ою)?\b|\bбісектрис(а|у|и|ою)?\b|\bвисот(а|у|и|ою)?\b"),
        ("POINT", r"[A-Z]"),
        ("DOT", r"\."),
        ("IGNORE", r"(?i)\bу\b|\bв\b"),
        ("WHITESPACE", r"\s+"),
    ]

    def __init__(self, text):
        self.tokens = self.lex(text)
        self.current_token = 0

    def lex(self, text):
        tokens = []
        while text:
            matched = False
            for token_type, pattern in self.TOKENS:
                regex = re.compile(pattern)
                match = regex.match(text)
                if match:
                    lexeme = match.group(0)
                    if token_type != "WHITESPACE" and token_type != "IGNORE":
                        tokens.append((token_type, lexeme))
                    text = text[len(lexeme):]
                    matched = True
                    break
            if not matched:
                raise ValueError(f"Unrecognized token: {text[:20]}")
        tokens.append(("EOF", ""))
        return tokens

    def match(self, expected_type):
        if self.tokens[self.current_token][0] == expected_type:
            token = self.tokens[self.current_token]
            self.current_token += 1
            return token
        else:
            raise SyntaxError(f"Expected {expected_type} but found {self.tokens[self.current_token]}")

    def parse(self):
        commands = []
        while self.tokens[self.current_token][0] != "EOF":
            commands.append(self.command())
            if self.tokens[self.current_token][0] == "DOT":
                self.match("DOT")
        return Node("Program", children=commands)

    def command(self):
        cmd_token = self.match("COMMAND")
        if cmd_token[1].lower() == "побудувати":
            triangle_type_node = []
            if self.tokens[self.current_token][0] in {"TYPE_SIDE", "TYPE_ANGLE"}:
                triangle_type_node.append(self.match(self.tokens[self.current_token][0]))

            if self.tokens[self.current_token][0] in {"TYPE_SIDE", "TYPE_ANGLE"}:
                triangle_type_node.append(self.match(self.tokens[self.current_token][0]))

            triangle_node = self.triangle()

            return Node("Command", cmd_token[1],
                        [Node("TriangleType", " ".join([t[1] for t in triangle_type_node])), triangle_node])

        elif cmd_token[1].lower() == "провести":
            element_node = self.element()
            triangle_node = self.triangle()
            return Node("Command", cmd_token[1], [element_node, triangle_node])

        elif cmd_token[1].lower() == "відмітити":
            element_node = self.element()
            point_node = self.match("POINT")
            self.match("FIGURE")
            triangle_node = self.triangle()
            return Node("Command", cmd_token[1],
                        [Node("Element", element_node[1]), Node("Point", point_node[1]), triangle_node])

        else:
            raise SyntaxError("Unknown command")

    def type_triangle(self):
        angle_type = None
        side_type = None

        if self.tokens[self.current_token][0] == "TYPE_ANGLE":
            angle_type = self.match("TYPE_ANGLE")
        if self.tokens[self.current_token][0] == "TYPE_SIDE":
            side_type = self.match("TYPE_SIDE")

        # Якщо є обидва типи
        if angle_type and side_type:
            return Node("TriangleType", value=f"{angle_type[1]} {side_type[1]}")
        # Якщо є лише один тип
        elif angle_type:
            return Node("TriangleType", value=angle_type[1])
        elif side_type:
            return Node("TriangleType", value=side_type[1])

        # Якщо є тільки "рівносторонній"
        elif self.tokens[self.current_token][0] == "TYPE_TRIANGLE":
            triangle_type = self.match("TYPE_TRIANGLE")
            return Node("TriangleType", value=triangle_type[1])
        else:
            raise SyntaxError("Expected type of triangle")

    def element(self):
        if self.tokens[self.current_token][0] == "ELEMENT":
            element_token = self.match("ELEMENT")

            first_point = self.match("POINT")
            second_point = self.match("POINT")

            return Node("ElementWithPoints", element_token[1], [
                Node("Point", first_point[1]),
                Node("Point", second_point[1])
            ])
        else:
            raise SyntaxError("Expected element followed by two points")

    def triangle(self):
        self.match("FIGURE")

        first_point = self.match("POINT")
        second_point = self.match("POINT")
        third_point = self.match("POINT")

        return Node("Triangle", value="".join([first_point[1], second_point[1], third_point[1]]))


text = """Побудувати довільний гострокутний трикутник ABC. 
Провести медіану AM в трикутнику ABC.
Провести медіану MK в трикутнику ABM.
"""
parser = Parser(text)
print(parser.tokens)
tree = parser.parse()
print(tree)

root_node = tree
drawer = DiagramDrawer(root_node)
drawer.draw()