import unittest

class ToposortTests(unittest.TestCase):

    def test_toposort(self):
        import random
        from geeksw.core import get_exec_order

        def get_word_list():
            import gzip
            import json

            with gzip.GzipFile("words.json.gz", 'r') as fin:
                json_bytes = fin.read()

            json_str = json_bytes.decode('utf-8')
            words = json.loads(json_str)["data"]

            return list(set(words))

        words = get_word_list()

        def take_random_word():
            i = random.randrange(0,len(words))
            word = words[i]
            del words[i]
            return word

        n = 100

        modules = {}
        all_products = []

        for i in range(n):
            products = [take_random_word()]
            requires = []
            if random.getrandbits(1):
                products += [take_random_word()]
            if all_products != []:
                while random.getrandbits(1):
                    requires += [random.choice(all_products)]
                requires = list(set(requires))
            name = "And".join([p.title() for p in products]) + "Producer"
            name = name.replace("-", "").replace(" ", "")
            modules[name] = {
                "produces" : products,
                "requires" : requires,
                }
            all_products += products

        exec_order = get_exec_order(modules)

        produced = []
        for name in exec_order:
            info = modules[name]
            for req in info["requires"]:
                assert req in produced
            produced += info["produces"]

if __name__ == '__main__':

    unittest.main(verbosity=2)
