class ProductError(Exception):
    """Базовый класс для обозночение всех ошибок связанных с продуктами"""
    
class ProductNotFindError(ProductError):
    """Базовый класс озночающий что продукт не обнаружен"""