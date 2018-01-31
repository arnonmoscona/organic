from unittest import TestCase

from free_range.core.common.dynamic import import_by_name
from free_range.core.common.exceptions import InvalidArgument, NotFoundError


class ImportByNameTests(TestCase):
    def test_loading_module_by_name_does_not_raise(self):
        import_by_name('os.path')

    def test_loading_by_name_returns_the_module(self):
        os_path = import_by_name('os.path')
        self.assertTrue(hasattr(os_path, 'realpath'))

    def test_can_load_a_module_with_no_dot_separators(self):
        os_module = import_by_name('os')
        self.assertTrue(hasattr(os_module, 'path'))

    def test_if_module_does_not_exist_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            import_by_name('os.junk')

    def test_if_module_does_not_exist_raises_not_found_no_dot_case(self):
        with self.assertRaises(NotFoundError):
            import_by_name('junk')

    def test_if_module_part_is_not_a_module_then_raises_invalid(self):
        with self.assertRaises(InvalidArgument):
            import_by_name('os.path.realpath.xxx')

    def test_leading_dot_raises_invalid(self):
        with self.assertRaises(InvalidArgument):
            import_by_name('.os.path')

    def test_trailing_dot_raises_invalid(self):
        with self.assertRaises(InvalidArgument):
            import_by_name('os.path.')

    def test_non_callable_raises_invalid(self):
        # This is the case when we load an argument type or a return type, for instance
        with self.assertRaises(InvalidArgument):
            import_by_name('free_range.core.common.tests.dynamic.loaded_dynamically.SOME_VAR',
                           require_callable=True)
