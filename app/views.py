from tabnanny import check
from unittest import result
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

from .decorators import unauthenticated_user, allowed_users

# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def main_register(request):
    return render(request, 'registration/register.html')

def register_user(request):
    context = {}
    status = ''
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        context['form'] = form

        #check if number exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE phone_num = %s", [request.POST['phone_number']])
            number = cursor.fetchone()
            if number != None:
                status = 'This number is already being used.'
                context['status'] = status
                return render(request, 'registration/registeruser.html', context)
                #return redirect("/register/user", context)
            else:
                pass
        
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            group = Group.objects.get(name='user')
            user.groups.add(group)
            messages.success(request, 'User account was created for ' + email)
            # POST request: create in users table
            if request.POST['action'] == 'register':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE email = %s", [request.POST['email']])
                    user = cursor.fetchone()
                ## No user with same id
                if user == None:
                    ##TODO: date validation
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", 
                                        [request.POST['full_name'], 
                                        request.POST['email'],
                                        request.POST['phone_number'] , 
                                        request.POST['location']])

                        # if there is skill input
                        if request.POST['skills']:
                            for skill in set(request.POST['skills'].split(sep = ', ')):
                                cursor.execute("INSERT INTO skills VALUES(%s, %s)", [request.POST['email'], skill])
                        
                        if request.POST['past_company'] and request.POST['past_dept'] and \
                            request.POST['past_title'] and request.POST['past_years']:          
                            cursor.execute("INSERT INTO past_exp VALUES(%s, %s, %s, %s, %s)",
                                [request.POST['email'], 
                                request.POST['past_company'], 
                                request.POST['past_dept'], 
                                request.POST['past_title'], 
                                request.POST['past_years']])
                        elif request.POST['past_company'] or request.POST['past_dept'] or \
                            request.POST['past_title'] or request.POST['past_years']:
                            status= 'Please complete the remaining details on your ex!'
                else: 
                    status = 'User with email %s already exists' % (request.POST['email'])
            return redirect("/login")
        else:
            messages.error(request, 'Invalid form submission')
    else:
        context['status'] = status
        context['form'] = CreateUserForm()
    return render(request, 'registration/registeruser.html', context)

def register_company(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            company = form.save()
            email = form.cleaned_data.get('email')
            group = Group.objects.get(name='company')
            company.groups.add(group)
            messages.success(request, 'Company account was created for ' + email)
            #POST request: create in company table
            with connection.cursor() as cursor:
                args = (request.POST['company_name'],
                        request.POST['industry'],
                        form.cleaned_data.get('email'))
                cursor.execute("INSERT INTO company VALUES(%s, %s, %s)", args)
            return redirect("/login")
        else:
            messages.error(request, 'Invalid form submission')
    else:
        form = CreateUserForm()
    # POST request: create in company table
    return render(request, 'registration/registercompany.html', {"form": form})

@unauthenticated_user
@allowed_users(allowed_roles=['user'])
def user_search(request):
    context = {}
    status = ''
    #Basic search
    if request.POST:
        if request.POST['action'] == 'search':
            with connection.cursor() as cursor:
                word = "%" + request.POST['search'].lower() + "%" #request.POST['search'].lower()
                cursor.execute("SELECT * FROM jobs WHERE (lower(descript) LIKE %s OR lower(job_title) LIKE %s OR lower(name) LIKE %s OR lower(dept) LIKE %s) \
                    OR (est_pay >= %s::INTEGER) \
                    OR (location = %s) AND expiry <= NOW()",
                [word, word, word, word, request.POST['value'],request.POST['location']])
                check = cursor.arraysize
                jobs = cursor.fetchall()
                check = len(jobs)
                result_dict = {'records': jobs}
            ## No result
            if check == 0:
                return redirect('/user/search/fail')
            else:
                return render(request, 'app/user/searchresult.html', result_dict)
    else:
        pass
    return render(request, 'app/user/usersearch.html')

#i dont think is used
@unauthenticated_user
@allowed_users(allowed_roles=['user'])
def user_search_result(request):
    result_dict = {}
    if request.POST:
        if request.POST['action'] == 'search':
            with connection.cursor() as cursor:
                word = '%' + request.POST['search'] + '%'
                cursor.execute("SELECT * FROM jobs WHERE (name LIKE %s OR job_title LIKE %s OR descript LIKE %s) or (est_pay >= %s::INTEGER) or (location = %s) and expiry <= NOW()",
                [word, word, word, request.POST['value'],request.POST['location']])
                jobs = cursor.fetchall()
                result_dict = {'records': jobs}
    return render(request, 'app/user/searchresult.html', result_dict)

@unauthenticated_user
@allowed_users(allowed_roles=['user'])
def search_fail(request):
    return render(request, 'app/user/searchfail.html')

@unauthenticated_user
def nav(request):
    return render(request,'app/nav.html')
    
@unauthenticated_user
@allowed_users(allowed_roles=['user'])
def user_home(request):
    email = request.user.email
    with connection.cursor() as cursor:
        cursor.execute("SELECT full_name FROM users WHERE email = %s", [email])
        name = cursor.fetchall()
    if request.POST:
        if request.POST['action'] == 'search':
            return redirect('/user/search')
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT j.name, j.job_title, j.descript, j.job_id FROM\
                        applications a, jobs j \
                        WHERE j.job_id = a.job_id and a.email = %s",\
                        [email])
        your_jobs = cursor.fetchall()

        #skill job
        cursor.execute("SELECT s.skill FROM skills s WHERE email = %s", [email])
        your_skills = cursor.fetchall()
        print(your_skills)
        if len(your_skills) == 0:
            skill = ""
        else:
            skill = '%' + str(your_skills[0][0]) + '%'
            print(skill)
        cursor.execute("SELECT * FROM jobs WHERE jobs.descript LIKE %s", [skill])
        skill_jobs = cursor.fetchall()

        #exp job (todo: debug)
        cursor.execute("SELECT p.job_title\
                    FROM past_exp p\
                    WHERE p.email = %s\
                    AND p.years >= ALL(\
                        SELECT p.years\
                        FROM past_exp p\
                        WHERE p.email = %s)", [email, email])

        prev_job = cursor.fetchall()
        if len(prev_job) == 0:
            exp_jobs = None
        else:
            job_title = '%' + str(prev_job[0][0]) + '%'
            cursor.execute("SELECT *\
                    FROM jobs j \
                    WHERE j.job_title LIKE %s", [job_title])
            exp_jobs = cursor.fetchall()

        #stats job
        ##Top 3 most popular skills among users
        cursor.execute("SELECT string_agg(s.skill,', ')\
            FROM(\
                SELECT s.skill, COUNT(*)\
                FROM skills s\
                GROUP BY s.skill\
                HAVING COUNT(*) = ANY(\
                    SELECT DISTINCT COUNT(*)\
                    FROM skills s\
                    GROUP BY s.skill\
                    LIMIT 3)\
                ORDER BY COUNT(*) DESC\
                LIMIT 3) s\
                ")
        pop_skills = cursor.fetchall()

        #most applied jobs
        cursor.execute("SELECT j.job_title, j.job_id\
            FROM jobs j, applications a\
            WHERE a.job_id = j.job_id\
            GROUP BY j.job_title, j.job_id\
            HAVING COUNT(*) >= ALL(\
                SELECT COUNT(*)\
                FROM jobs j, applications a\
                WHERE a.job_id = j.job_id\
                GROUP BY j.job_title)")
        demand_job = cursor.fetchone()

    result_dict = {'name':name, 'your_jobs': your_jobs, 'exp_jobs': exp_jobs, 'skill_jobs': skill_jobs,
        'pop_skills': pop_skills, 'demand_job': demand_job}

    return render(request,'app/user/userhome.html', result_dict)

@unauthenticated_user
@allowed_users(allowed_roles=['user'])
def user_profile(request, id):
    result_dict = {}
    status = ''
    email = request.user.email
    with connection.cursor() as cursor:
        if request.POST:
            if request.POST['action'] == 'done':
                return redirect('/user')
            
            elif request.POST['action'] == 'delete':
                cursor.execute("DELETE FROM applications\
                                    WHERE email = %s;\
                                DELETE FROM past_exp\
                                    WHERE email = %s;\
                                DELETE FROM skills\
                                    WHERE email = %s;\
                                DELETE FROM users\
                                    WHERE email = %s;", [email,email,email,email])
                cursor.execute("DELETE FROM app_user_groups WHERE user_id = (\
                                    SELECT id FROM app_user WHERE email = %s);\
                                DELETE FROM app_user WHERE email = %s;", [email, email])                              
                return redirect('/login')

            elif request.POST['action'] == 'update_loc':
                cursor.execute("UPDATE users SET location = %s WHERE email = %s", [request.POST['location'], email])

            elif request.POST['action'] == 'update_skills':
                #check if this skill already exists
                cursor.execute("SELECT * FROM skills WHERE email = %s AND skill = %s", [email, request.POST['skills']])
                if cursor.fetchone():
                    status = "Seems like you have already mastered this skill!"
                    pass
                else:
                    cursor.execute("INSERT INTO skills VALUES (%s, %s)", [email, request.POST['skills']])
            elif request.POST['action'] == 'update_ex':
                #check if this ex already exists
                cursor.execute("SELECT * FROM past_exp WHERE email = %s AND company_name = %s AND dept = %s AND job_title = %s"\
                    , [email, request.POST['past_company'], request.POST['past_dept'], request.POST['past_title']])
                if cursor.fetchone():
                    status = "Miss your Ex?"
                    pass
                else:
                    if request.POST['past_company'] and request.POST['past_dept'] and \
                                request.POST['past_title'] and request.POST['past_years']:          
                                cursor.execute("INSERT INTO past_exp VALUES(%s, %s, %s, %s, %s)",
                                    [email, 
                                    request.POST['past_company'], 
                                    request.POST['past_dept'], 
                                    request.POST['past_title'], 
                                    request.POST['past_years']])
                    elif request.POST['past_company'] or request.POST['past_dept'] or \
                        request.POST['past_title'] or request.POST['past_years']:
                        status= 'Please complete the remaining details on your ex!'

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cursor.fetchall()[0]
        
        cursor.execute("SELECT skill FROM skills WHERE email = %s", [email])
        skill = [x[0] for x in cursor.fetchall()]
        if len(skill) == 0:
            skills = ''
        else:
            skills = ', '.join(skill)
        
        cursor.execute("SELECT * FROM past_exp WHERE email = %s", [email])
        records = cursor.fetchall()
        if len(records) == 0:
            records = None
        else:
            pass
    
    result_dict = {'user': user, 'skills': [skills], 'records': records, 'status':status}
    return render(request,'app/user/viewself.html', result_dict)

@unauthenticated_user
@allowed_users(allowed_roles=['company'])
def company_home(request):
    email = request.user.email
    if request.POST:
        ## Delete job
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                # need drop cascade foreign keys
                cursor.execute("DELETE FROM jobs WHERE job_id = %s", [request.POST['id']]) 
        ## Delete account
        elif request.POST['action'] == 'delete_account':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM applications\
                                WHERE job_id = ANY(\
                                    SELECT job_id\
                                    FROM jobs\
                                    WHERE email = %s);\
                                DELETE FROM jobs\
                                WHERE email = %s;\
                                DELETE FROM company\
                                WHERE email = %s;", [email,email,email])
                cursor.execute("DELETE FROM app_user_groups WHERE user_id = (\
                                SELECT id FROM app_user WHERE email = %s);\
                                DELETE FROM app_user WHERE email = %s;", [email, email])                              
                return redirect('/login')

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        company = request.user.email
        cursor.execute("SELECT * FROM jobs WHERE email = %s", [company])
        jobs_by_company = cursor.fetchall()
    result_dict = {'jobs_by_company': jobs_by_company}

    return render(request,'app/company/companyhome.html', result_dict)

@unauthenticated_user
@allowed_users(allowed_roles=['user'])
def user_view_job(request, id):
    context={}
    status=""
    email = request.user.email
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM applications WHERE email = %s and job_id = %s",
            [email, id])
        check = cursor.fetchone()

        if check == None:
            applied = False
            context['applied'] = applied
        else:
            applied = True
            context['applied'] = applied

    if request.POST:
        if request.POST['action'] == 'search':
            return redirect('/user/search')
        elif request.POST['action'] == 'apply':
            #check if already have
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM applications WHERE email = %s and job_id = %s",
                                [email, request.POST['job_id']])
                check = cursor.fetchone()
            if check == None:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO applications VALUES (%s, %s)", [email, request.POST['job_id']])
                return redirect('/user/job/view/'+str(id))
            else:
                status = 'You have already applied for this job'
        elif request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM applications WHERE email = %s and job_id = %s",
                                [email, request.POST['job_id']])
                check = cursor.fetchone()
            if check == None:
                status = "this shouldn't exist"
            else:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM applications WHERE email = %s AND job_id = %s", [email, request.POST['job_id']])
                return redirect('/user/job/delete')

    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", [id])
        job = cursor.fetchone()


    #Stats: total num applications
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*)\
        FROM applications a, jobs j\
        WHERE a.job_id = j.job_id\
        AND a.job_id = %s", [id])
        count = cursor.fetchone()
    
    #skill_counts
    with connection.cursor() as cursor:
        cursor.execute("SELECT s.skill, COUNT(*)\
            FROM applications a NATURAL JOIN skills s LEFT OUTER JOIN jobs j ON a.job_id = j.job_id\
            WHERE s.skill IN (\
                SELECT s.skill\
                FROM skills s\
                WHERE s.email = %s) \
            AND j.job_id = %s \
            GROUP BY s.skill", [email, id])
        comp_skills = cursor.fetchall()

    #skillz
    with connection.cursor() as cursor:
        cursor.execute("SELECT string_agg(s.skill, ', ')\
            FROM (\
                SELECT DISTINCT LOWER(s.skill) skill, COUNT(*)\
                FROM skills s NATURAL JOIN applications a, jobs j\
                WHERE a.job_id = j.job_id\
                AND a.job_id = %s\
                GROUP BY LOWER(s.skill)\
                ORDER BY COUNT(*) DESC\
                LIMIT 5) s", [id])
        skillz = cursor.fetchall()

    # graph: Average job pay for skills you have
    with connection.cursor() as cursor:
        label_query = "SELECT s.skill "\
                        "FROM skills s , jobs j "\
                        "WHERE j.descript LIKE '%' || s.skill || '%' "\
                        "AND s.email = '{}' "\
                        "GROUP BY s.skill".format(email)
        cursor.execute(label_query)

        labels = cursor.fetchall()
        if labels == None:
            graph_labels = None
        else:
            graph_labels = [x[0] for x in labels]

        value_query = "SELECT TRUNC(AVG(j.est_pay)) as avg_pay "\
                "FROM skills s , jobs j "\
                "WHERE j.descript LIKE '%' || s.skill || '%' "\
                "AND s.email = '{}' "\
                "GROUP BY s.skill".format(email)

        cursor.execute(value_query)
        
        values = cursor.fetchall()
        if values == None:
            graph_values = None
        else:
            graph_values = [int(x[0]) for x in values]

    colorPalette = ['rgba(255, 99, 132, 0.2)', 
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)']
    graph_colours = []
    i = 0
    while i < len(colorPalette) and len(graph_colours) < len(graph_labels):
        graph_colours.append(colorPalette[i])
        i += 1
        if i == len(colorPalette) and len(graph_colours) < len(graph_labels):
            i = 0
    
    context['status'] = status
    context['job'] = job
    context['count'] = count
    context['comp_skills'] = comp_skills
    context['skillz'] = skillz
    context['graph_labels'] = graph_labels
    context['graph_values'] = graph_values
    context['graph_colours'] = graph_colours

    return render(request,'app/user/viewjob.html', context)

def user_apply_job(request):
    pass
    email = request.user.email
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO applications VALUES (%s, %s::INTEGER)", [email, request.POST[2]])
    return render(request, '')

def user_job_success(request):
    return render(request, 'app/user/applysuccess.html')

def user_job_delete(request):
    return render(request, 'app/user/deletesuccess.html')

@unauthenticated_user
def company_view_job(request, id):
    ## Use raw query to get job
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", [id])
        job = cursor.fetchone()
    result_dict = {'job': job}

    return render(request,'app/company/viewjob.html', result_dict)  

@unauthenticated_user
@allowed_users(allowed_roles=['company'])
def add_job(request):
    context = {}
    status = ''

    if request.POST:
        ## Check if job already exist in the table pkey: (email, job_title, dept)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs WHERE email = %s AND job_title = %s AND dept = %s", 
                            [request.user.email, 
                            request.POST['job_title'],
                            request.POST['dept']])
            job = cursor.fetchone()
            ## No job with same pkey
            if job == None:
                cursor.execute("SELECT name FROM company WHERE email = %s", [request.user.email])
                company_name = cursor.fetchone()
                if request.POST['est_pay'] == '':
                    est_pay = None
                else:
                    est_pay = request.POST['est_pay']

                query = "INSERT INTO jobs(name, email, job_title, descript, dept, est_pay, location, expiry) "\
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, 
                            [company_name, 
                            request.user.email, 
                            request.POST['job_title'],
                            request.POST['descript'] , 
                            request.POST['dept'], 
                            est_pay, 
                            request.POST['location'], 
                            request.POST['expiry']])
                return redirect('/company')    
            else:
                status = 'Job with company email %s, job_title %s and dept %s already exists' % (request.POST['email'], request.POST['job_title'], request.POST['dept'])
    context['status'] = status
 
    return render(request, "app/company/addjob.html", context)

@unauthenticated_user
@allowed_users(allowed_roles=['company'])
def edit_job(request, id):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        with connection.cursor() as cursor:
            if request.POST['est_pay'] == '':
                # original val
                est_pay = obj[6]
            else:
                est_pay = request.POST['est_pay']

            if request.POST['expiry'] == '':
                expiry = obj[8]
            else:
                expiry = request.POST['expiry']

            cursor.execute(
                "UPDATE jobs\n"\
                "SET name = CASE WHEN %s != '' THEN %s ELSE name END, "\
	                "job_title = CASE WHEN %s != '' THEN %s ELSE job_title END, "\
                    "descript = CASE WHEN %s != '' THEN %s ELSE descript END, "\
                    "dept = CASE WHEN %s != '' THEN %s ELSE dept END, "\
                    "est_pay = %s, "\
                    "location = CASE WHEN %s != '' THEN %s ELSE location END, "\
                    "expiry = %s\n"\
                "WHERE job_id = %s", 
                    [request.POST['name'], request.POST['name'],
                    request.POST['job_title'], request.POST['job_title'],
                    request.POST['descript'], request.POST['descript'],
                    request.POST['dept'], request.POST['dept'],
                    est_pay,
                    request.POST['location'], request.POST['location'],
                    expiry,
                    id]
                )
            status = 'Job edited successfully!'
            cursor.execute("SELECT * FROM jobs WHERE job_id = %s", [id])
            obj = cursor.fetchone()

    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/company/editjob.html", context)

@unauthenticated_user
@allowed_users(allowed_roles=['company'])
def view_applicants(request, id):
    ## Use raw query to get a customer
    # Applicant with most skills
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM jobs WHERE job_id = %s", [id])
        job = cursor.fetchone()

    with connection.cursor() as cursor:
        most_skills_query = "SELECT * \
            FROM users u NATURAL JOIN (\
                SELECT s.email, string_agg(s.skill, ', ') AS all_skills \
                    FROM skills s \
                    GROUP BY s.email) s LEFT OUTER JOIN past_exp USING (email)\
            WHERE email IN (\
                SELECT email \
                    FROM skills NATURAL JOIN applications\
                    WHERE job_id = %s\
            GROUP BY email \
            HAVING COUNT(*) >= ALL(\
                SELECT COUNT(*) as num_skills \
                    FROM skills NATURAL JOIN applications \
                    WHERE job_id = %s\
                GROUP BY email))"
        cursor.execute(most_skills_query, [id, id])
        most_skills = cursor.fetchall()
    
    #All applicants
    with connection.cursor() as cursor:
        all_applicants_query = "SELECT * "\
                "FROM ("\
                        "SELECT s.email, string_agg(s.skill, ', ') AS all_skills "\
                        "FROM skills s "\
                        "GROUP BY s.email"\
                    ") s "\
                "LEFT OUTER JOIN past_exp USING (email) "\
                "LEFT OUTER JOIN users USING (email) "\
                "WHERE email IN (SELECT email FROM applications WHERE job_id = %s)"
        cursor.execute(all_applicants_query, [id])
        all_applicants = cursor.fetchall()
    result_dict = {'job': job, 'most_skills': most_skills, 'all_applicants': all_applicants}

    return render(request,'app/company/viewapplicants.html', result_dict)