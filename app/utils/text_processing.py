import re
from typing import List


def clean_text(text: str) -> str:
    """
    Limpiar texto eliminando caracteres especiales y normalizando espacios
    """
    # Eliminar caracteres de control excepto saltos de línea
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar espacios al inicio y final
    text = text.strip()
    
    return text


def extract_code_blocks(text: str) -> List[str]:
    """
    Extraer bloques de código del texto
    """
    # Buscar bloques de código con markdown
    code_pattern = r'```(?:\w+)?\n(.*?)\n```'
    matches = re.findall(code_pattern, text, re.DOTALL)
    
    return [match.strip() for match in matches]


def is_code_like(text: str) -> bool:
    """
    Determinar si un texto parece ser código
    """
    code_indicators = [
        'def ', 'class ', 'import ', 'from ', 'if __name__',
        'function', 'var ', 'const ', 'let ', 'return ',
        'for ', 'while ', 'if ', 'else:', 'elif ',
        'try:', 'except:', 'finally:', 'with ',
        'async def', 'await ', 'async with'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in code_indicators)


def split_into_sentences(text: str) -> List[str]:
    """
    Dividir texto en oraciones
    """
    # Patrón para dividir en oraciones
    sentence_pattern = r'[.!?]+'
    sentences = re.split(sentence_pattern, text)
    
    # Limpiar y filtrar oraciones vacías
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extraer palabras clave del texto
    """
    # Eliminar caracteres especiales y convertir a minúsculas
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Dividir en palabras
    words = clean_text.split()
    
    # Filtrar palabras comunes (stop words básicas)
    stop_words = {
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'pero', 'sus', 'me', 'hasta', 'hay', 'donde', 'han', 'quien', 'están', 'estado', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros'
    }
    
    # Filtrar palabras cortas y stop words
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    # Contar frecuencia
    from collections import Counter
    word_counts = Counter(keywords)
    
    # Obtener las palabras más frecuentes
    return [word for word, count in word_counts.most_common(max_keywords)] 