"""In this file tests for Writer scripts are gathered."""
import os
import tempfile

import pytest

from writer import XMLWriter, CSVWriter, WriterManager


class WriterMixin:
    """Mixin for Writer test classes."""

    @classmethod
    def setup_class(cls):
        """Creates output file in temp path for tests purposes."""
        cls.outfile_path = tempfile.mkstemp(suffix='.csv')[1]

    @classmethod
    def teardown_class(cls):
        """Removes created file"""
        os.remove(cls.outfile_path)


class TestCSVWriter(WriterMixin):
    writer = CSVWriter

    @pytest.mark.parametrize('file_name,expected', [
        ('test.csvv', False),
        ('test.csv', True),
    ])
    def test_supporting_ext(self, file_name, expected):
        writer = self.writer(file_name)
        assert writer.check() == expected

    def test_save(self):
        writer = self.writer(self.outfile_path)
        writer.save(['abc', 'def', 'ghi'])
        expected = 'url\nabc\ndef\nghi\n'
        with open(self.outfile_path, 'rb') as result:
            assert result.read().decode('utf-8') == expected


class TestXMLWriter(WriterMixin):
    writer = XMLWriter

    @pytest.mark.parametrize('file_name,new_name', [
        ('test.xxml', 'test.xxml.xml'),
        ('test.xml', 'test.xml'),
    ])
    def test_supporting_extension(self, file_name, new_name):
        writer = self.writer(file_name)
        assert writer.check()
        assert writer.file_name == new_name

    def test_save(self):
        writer = self.writer(self.outfile_path)
        writer.save(['1', '2', '3'])
        expected = '' \
                   '<?xml version="1.0" encoding="UTF-8"?>\n' \
                   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' \
                   '  <url>\n    <loc>1</loc>\n  </url>\n' \
                   '  <url>\n    <loc>2</loc>\n  </url>\n' \
                   '  <url>\n    <loc>3</loc>\n  </url>\n' \
                   '</urlset>'
        with open(self.outfile_path, 'rt') as result:
            assert result.read() == expected


@pytest.mark.usefixtures('mocker')
class TestWriterManager:

    def test_select_csv_writer(self):
        manager = WriterManager('test.csv')
        assert isinstance(manager.writer, CSVWriter)

    def test_select_xml_writer(self):
        manager = WriterManager('test.xml')
        assert isinstance(manager.writer, XMLWriter)

    def test_select_xml_writer_by_default(self):
        manager = WriterManager('test.csvvv')
        assert isinstance(manager.writer, XMLWriter)

    def test_skip_writing_when_no_data(self, mocker):
        save_mck = mocker.patch('writer.CSVWriter.save')
        manager = WriterManager('test.csv')
        manager.export_data([])
        assert not save_mck.called

    @pytest.mark.parametrize('data', [
        [1, 2, 3],  # list
        (1, 2, 3),  # tuple
        {1, 2, 3},  # set
    ])
    def test_writing_with_data(self, mocker, data):
        save_mck = mocker.patch('writer.CSVWriter.save')
        manager = WriterManager('test.csv')
        manager.export_data(data)
        assert save_mck.called
        assert save_mck.call_args_list[0][0][0] == data

    def test_skip_writing_with_string(self, mocker):
        save_mck = mocker.patch('writer.CSVWriter.save')
        manager = WriterManager('test.csv')
        with pytest.raises(AttributeError):
            manager.export_data('1, 2, 3')
        assert not save_mck.called
