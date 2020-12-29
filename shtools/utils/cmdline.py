# -*- coding: utf-8 -*-


# CommandLineToArgvW
class CmdLine(object):
    @staticmethod
    def to_list(commandLine):
        tokens = []
        token = ""
        sections = commandLine.split(" ")

        curPart = 0
        while curPart < len(sections):
            # We are in a quoted section!!
            if sections[curPart].startswith('"'):
                # remove leading "
                token += sections[curPart][1:]
                quoteCount = 0
                # Step backwards from the end of the current section to find the count of quotes from the end.
                # This will exclude looking at the first character, which was the " that got us here in the first place.
                while quoteCount < len(sections[curPart]) - 1:
                    if sections[curPart][len(sections[curPart]) - 1 - quoteCount] != '"':
                        break
                    quoteCount += 1
                # if we didn't have a leftover " (i.e. the 2N+1), then we should continue adding in the next section to the current token.
                while quoteCount % 2 == 0 and curPart != len(sections) - 1:
                    quoteCount = 0
                    curPart += 1
                    # Step backwards from the end of the current token to find the count of quotes from the end.
                    while quoteCount < len(sections[curPart]):
                        if sections[curPart][len(sections[curPart]) - 1 - quoteCount] != '"':
                            break
                        quoteCount += 1

                    token += " " + sections[curPart]
                # remove trailing " if we had a leftover
                # if we didn't have a leftover then we go to the end of the command line without an enclosing "
                # so it gets treated as a quoted argument anyway
                if quoteCount % 2 != 0:
                    token = token[:-1]
                token = token.replace('""', '"')
            else:
                # Not a quoted section so this is just a boring parameter
                token += sections[curPart]
            # strip whitespace (because).
            if token.strip():
                tokens.append(token)
            token = ""
            curPart += 1
        # remove the first argument.  This is the executable details.
        # tokens.RemoveAt(0);

        # return the array in the same format args[] usually turn up to main in.
        return tokens


if __name__ == "__main__":
    print(CmdLine.to_list('ssh 10.25.83.110 -u root --password Paic1234 "ping 127.0.0.1 -c 5"     "xx"X YYY"'))
    print(CmdLine.to_list('curl "http://www.baidu.com/"a&b c" -X POST -d "nc -z -v -u 10.25.83.110 123"'))
