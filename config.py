token = "5807450334:AAEBL7_eV4OcY4C4_HrpVJa2zdGa8G2QDlo"
jssript = '''
    <script >
    document.getElementById("cbtype").onchange = function() {
        fetch("http://127.0.0.1:8000/", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "idtype": document.getElementById("cbtype").value,
                "idtm": document.getElementById("cbid").value
            })
        }).then(response => response.json()).then(response => console.log(JSON.stringify(response)))
    };
    document.getElementById("cbid").onchange = function() {
        fetch("http://127.0.0.1:8000/", {
           method: "GET",
           headers: {
            "idtype": document.getElementById("cbtype").value,
            "idtm": document.getElementById("cbid").value
        }
    }).
    then(response => response.json()).then(response => console.log(JSON.stringify(response)))
}; </script>'''