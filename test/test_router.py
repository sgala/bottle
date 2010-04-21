import unittest
import bottle

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.r = r = bottle.Router()

    def testBasic(self):
        add = self.r.add
        match = self.r.match
        def basic(spec, handler, url, bindings):
            route = bottle.Route(spec, handler)
            add(route)
            self.assertEqual((route, bindings), match(url))
        basic('/static', 'static', '/static', {})
        basic('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'handler', '/:its/a/cruel/world/', {'test': 'cruel', 'name': 'world'})
        basic('/:test', 'notail', '/test', {'test': 'test'})
        basic(':test/', 'nohead', 'test/', {'test': 'test'})
        basic(':test', 'fullmatch', 'test', {'test': 'test'})
        basic('/:#anon#/match', 'anon', '/anon/match', {})
        self.assertEqual((None, {}), match('//no/m/at/ch/'))

    def testParentheses(self):
        add = self.r.add
        match = self.r.match
        def basic(spec, handler, url, bindings, fit=True):
            route = bottle.Route(spec, handler)
            add(route)
            if fit:
                self.assertEqual((route, bindings), match(url))
            else:
                self.assertEqual((None, {}), match(url))
        basic('/func(:param)', 'func', '/func(foo)', {'param':'foo'})
        basic('/func2(:param#(foo|bar)#)', 'func2', '/func2(foo)', {'param':'foo'})
        basic('/func2(:param#(foo|bar)#)', 'func2', '/func2(bar)', {'param':'bar'})
        basic('/func2(:param#(foo|bar)#)', 'func2', '/func2(baz)', {}, fit=False)
        basic('/groups/:param#(foo|bar)#', 'groups', '/groups/foo', {'param':'foo'})

    def testErrorInPattern(self):
        self.assertRaises(bottle.RouteSyntaxError, self.r.add, '/:bug#(#/', 'buggy')

    def testBuild(self):
        add = self.r.add
        build = self.r.build
        add('/:test/:name#[a-z]+#/', 'handler', name='testroute')
        add('/anon/:#.#', 'handler', name='anonroute')
        url = build('testroute', test='hello', name='world')
        self.assertEqual('/hello/world/', url)
        self.assertRaises(bottle.RouteBuildError, build, 'test')
        # RouteBuildError: No route found with name 'test'.
        self.assertRaises(bottle.RouteBuildError, build, 'testroute')
        # RouteBuildError: Missing parameter 'test' in route 'testroute'
        #self.assertRaises(bottle.RouteBuildError, build, 'testroute', test='hello', name='1234')
        # RouteBuildError: Parameter 'name' does not match pattern for route 'testroute': '[a-z]+'
        #self.assertRaises(bottle.RouteBuildError, build, 'anonroute')
        # RouteBuildError: Anonymous pattern found. Can't generate the route 'anonroute'.

if __name__ == '__main__':
    unittest.main()
