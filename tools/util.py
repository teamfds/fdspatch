import re
from typing import cast, overload

@overload
def rgx_search(pattern: str | re.Pattern[str], string: str, groups: None = None) -> str | None: ...
@overload
def rgx_search(pattern: str | re.Pattern[str], string: str, groups: int) -> str | None: ...
@overload
def rgx_search(pattern: str | re.Pattern[str], string: str, groups: list[int]) -> tuple[str, ...] | None: ...
def rgx_search(pattern: str | re.Pattern[str], string: str, groups: int | list[int] | None = None):
    if match := re.search(pattern, string):
        if groups is None:
            return match.group()  
        
        if isinstance(groups, int):
            return cast(str, match.group(groups))
            
        return cast(tuple[str, ...], match.group(*groups))

@overload
def rgx_search_nn(pattern: str | re.Pattern[str], string: str, groups: None = None) -> str: ...
@overload
def rgx_search_nn(pattern: str | re.Pattern[str], string: str, groups: int) -> str: ...
@overload
def rgx_search_nn(pattern: str | re.Pattern[str], string: str, groups: list[int]) -> tuple[str, ...]: ...
def rgx_search_nn(pattern: str | re.Pattern[str], string: str, groups: int | list[int] | None = None):
    match = cast(re.Match[str], re.search(pattern, string))
    
    if groups is None:
        return match.group()  
    
    if isinstance(groups, int):
        return cast(str, match.group(groups))
        
    return cast(tuple[str, ...], match.group(*groups))