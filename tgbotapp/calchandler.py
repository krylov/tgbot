class CalcHandler:

    def make_response(self, message):
        try:
            n = int(message.text)
            response = str(n*n)
        except:
            response = "This is not number"

        return response
