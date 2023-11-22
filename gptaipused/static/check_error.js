function 문장분류하기(){    
    let 문법오류리스트 = ["syntax", "not sysntax", "invalid", "EOL", "string literal", "Invalid syntax",
    "Unexpected token", "quotes", "brackets", "Missing parentheses", "Invalid indentation","Missing colon",
    "Invalid operator", "Invalid character", "Unexpected end of input", "Unexpected keyword", "EOL while scanning string literal"];
    let 예외오류리스트 = ["ZeroDivisionError", "FileNotFoundError", "TypeError", "ValueError", "IndexError", "KeyError", "ImportError", "NameError",
    "AttributeError", "NotImplementedError"];
    let 네임오류리스트 = ["name", "not defined", "NameError", "subscriptable", "object has no attribute", "not defined as a module",
    "not callable", "global name", "referenced before assignment", "local variable", "undefined variable"];
    let 타입오류리스트 = ["unsupported operand type(s)", "can only concatenate", "unsupported operand type(s) for +:", "object is not iterable", "object is not subscriptable", "argument must be", "is not a function", "is not a class", "is not a module", "is not a type"];
    let 인덱스오류리스트 = ["IndexError", "리스트", "range", "범위", "접근할 수 없음", "인덱스", "list", "tuple", "out of range","string index", 
    "assignment index", "does not support indexing", "is not subscriptable", "slice indices must be integers or None or have an index method"];
    let 속성오류리스트 = ["object has no attribute 'getitem'", "has no attribute 'setitem'", "object has no attribute 'iter'", "has no attribute 'append'", 
    "has no attribute 'split'", "has no attribute 'read'", "has no attribute 'write'", "has no attribute 'close'"];
    let 파일오류리스트 = ["No such file or directory", "Permission denied", "Is a directory", "IOError", "File not found", "File exists", "Unable to open file", "Cannot write to file", "Cannot read file", "File is locked"]
    

    let sentence = document.querySelector("#resultPrintLabel").value; //데이터 가져오기

    console.log(sentence);


    function 문법오류체크(text, 문법오류리스트) {
        return 문법오류리스트.some(function(문법오류리스트_값) {
            return text.includes(문법오류리스트_값);
        });
    }

    function 예외오류체크(text, 예외오류리스트) {
        return 예외오류리스트.some(function(예외오류리스트_값) {
            return text.includes(예외오류리스트_값);
        });
    }

    function 네임오류체크(text, 네임오류리스트) {
        return 네임오류리스트.some(function(네임오류리스트_값) {
            return text.includes(네임오류리스트_값);
        });
    }

    function 타입오류체크(text, 타입오류리스트) {
        return 타입오류리스트.some(function(타입오류리스트_값) {
            return text.includes(타입오류리스트_값);
        });
    }

    function 인덱스오류체크(text, 인덱스오류리스트) {
        return 인덱스오류리스트.some(function(인덱스오류리스트_값) {
            return text.includes(인덱스오류리스트_값);
        });
    }

    function 속성오류체크(text, 속성오류리스트) {
        return 속성오류리스트.some(function(속성오류리스트_값) {
            return text.includes(속성오류리스트_값);
        });
    }

    function 파일오류체크(text, 파일오류리스트) {
        return 파일오류리스트.some(function(파일오류리스트_값) {
            return text.includes(파일오류리스트_값);
        });
    }

    if ( 문법오류체크(sentence, 문법오류리스트))
    {
        return [document.querySelector('label#resultPrintLabel').innerHTML = "문법오류", document.querySelector("#resultPrintLabel").innerHTML = "문법오류"];
    }
    else if (예외오류체크(sentence, 예외오류리스트) )
    {
        return document.querySelector('label#resultPrintLabel').innerHTML = "입력된 값은" + sentence +  "입니다." + "<br><br>분석 결과 : 예외 오류 입니다";
    }
    else if (네임오류체크(sentence, 네임오류리스트) )
    {
        return document.querySelector('label#resultPrintLabel').innerHTML = "입력된 값은" + sentence +  "입니다." + "<br><br>분석 결과 : 네임 오류 입니다";
    }
    else if (타입오류체크(sentence, 타입오류리스트) )
    {
        return document.querySelector('label#resultPrintLabel').innerHTML = "입력된 값은" + sentence +  "입니다." + "<br><br>분석 결과 : 타입 오류 입니다";
    }
    else if (인덱스오류체크(sentence, 인덱스오류리스트) )
    {
        return document.querySelector('label#resultPrintLabel').innerHTML = "입력된 값은" + sentence +  "입니다." + "<br><br>분석 결과 : 리스트 인덱스 오류 입니다";
    }
    else if (속성오류체크(sentence, 속성오류리스트) )
    {
        return document.querySelector('label#resultPrintLabel').innerHTML = "입력된 값은" + sentence +  "입니다." + "<br><br>분석 결과 : 속성 오류 입니다";
    }
    else if (파일오류체크(sentence, 파일오류리스트) )
    {
        return document.querySelector('label#resultPrintLabel').innerHTML = "입력된 값은" + sentence +  "입니다." + "<br><br>분석 결과 : 파일 오류 입니다";
    }   
    else{
        return document.querySelector('label#resultPrintLabel').innerHTML = "입력된 값은" + sentence + "입니다." + "<br><br>분석 결과 : 알 수 없는 오류 입니다";
    }  
}



document.getElementById('postLink').addEventListener('click', function(e) {
    e.preventDefault(); // 기본 링크 동작 방지
    
    // XMLHttpRequest 또는 Fetch API를 사용하여 POST 요청 보내기
    fetch('http://minsubak.iptime.org:8000/ask', {
        method: 'POST',
        body: JSON.stringify({ key: 'value' }), // POST 데이터를 JSON 형식으로 전송 (필요에 따라 수정)
        headers: {
            'Content-Type': 'application/json' // POST 데이터의 형식 지정 (필요에 따라 수정)
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text(); // 응답 데이터를 텍스트로 읽기
    })
    .then(data => {
        // 응답 데이터를 이용하여 작업 수행
        document.querySelector('iframe[name="show_contents"]').src = `data:text/html;base64,${btoa(data)}`;
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
});