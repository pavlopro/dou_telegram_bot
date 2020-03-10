

def create_url(pro_lang, exp, city):
    if pro_lang == "Front End":
        pro_lang = "Front%20End"
    elif pro_lang == "C++":
        pro_lang = 'C%2B%2B'
    elif pro_lang == "Project Manager":
        pro_lang = 'Project%20Manager'
    elif pro_lang == "Product Manager":
        pro_lang = 'Product%20Manager'
    elif pro_lang == "Data Science":
        pro_lang = 'Data+Science'
    elif pro_lang == "ERP/CRM":
        pro_lang = 'ERP%2FCRM'
    elif pro_lang == "React Native":
        pro_lang = 'React+Native'
    elif pro_lang == "Technical Writer":
        pro_lang = 'Technical+Writer'
    elif pro_lang == "Системный администратор":
        pro_lang = 'Системный+администратор'

    if exp == '< 1 року':
        exp = '0-1'
    elif exp == '1…3 роки':
        exp = '1-3'
    elif exp == '3…5 років':
        exp = '3-5'
    elif exp == '5+ років':
        exp = '5plus'

    url = f"https://jobs.dou.ua/vacancies/?city={city}&category={pro_lang}&exp={exp}"
    return url
