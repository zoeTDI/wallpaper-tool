from .base_service import BaseService
from .export_service import ExportService
from .filter_service import FilterService


class WallpaperService:
    def __init__(self):
        self.base = BaseService()
        self.filter = FilterService()
        self.exporter = ExportService()

    # 代理调用
    def scan_directory(self, path):
        return self.base.scan(path)

    def filter_data(self, type_val, age_val):
        return self.filter.execute(self.base.data, type_val, age_val)

    def export_single(self, title, path):
        return self.exporter.export(title, path)
