
from django.shortcuts import render,redirect
from django.views.generic import View,FormView,TemplateView,ListView,DetailView,UpdateView,CreateView
from todo.forms import RegistrationForm,LoginForm,TaskForm,TaskChangeForm,PasswordResetForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from todo.models import Tasl
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy


def signin_required(fn):
    def wrapper(request,*args,**kargs):
        if not request.user.is_authenticated:
            messages.error(request,"you must login to perform this action")
            return redirect("signin")
        return fn(request,*args,**kargs)
    return wrapper

# Create your views here.
class SignupView(CreateView):
    model=User
    form_class=RegistrationForm
    template_name="register.html"
    success_url=reverse_lazy("signin")

    def form_valid(self, form):
        messages.success(self.request,"account created")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,"failed to create account")
        return super().form_invalid(form)
    # def get(self,request,*args,**kargs):
    #     form=self.form_class
    #     return render(request,self.template_name,{"form":form})
    # def post(self,request,*args,**kargs):
    #     form=self.form_class(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request,"account has been created")
    #         return redirect("signin")
    #     messages.error(request,"failed to create account")
    #     return render(request,self.template_name,{"form":form})

class SigninView(View):
    model=User
    template_name="login.html"
    form_class=LoginForm

    def get(self,request,*args,**kargs):
        form=self.form_class
        return render(request,self.template_name,{"form":form})
    
    def post(self,request,*args,**kargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            usname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=usname,password=pwd)
            if usr:
                login(request,usr)
                messages.success(request,"login success")
                return redirect("index")
            messages.error(request,"invalid credential")
            return render(request,self.template_name,{"form":form})

@method_decorator(signin_required,name="dispatch")       
class IndexView(TemplateView):
    template_name="index.html"

    # def get(self,request,*args,**kargs):
    #     return render(request,self.template_name)

@method_decorator(signin_required,name="dispatch")    
class TaskCreateView(CreateView):
    model=Tasl
    form_class=TaskForm
    template_name="task-add.html"
    success_url=reverse_lazy("task-list")

    #to add extra details in form before save
    def form_valid(self, form):
        form.instance.user=self.request.user
        
        messages.success(self.request,"todo has been created")
        return super().form_valid(form)

    # def get(self,request,*args,**kargs):
    #     form=self.form_class
    #     return render(request,self.template_name,{"form":form})
    
    # def post(self,request,*args,**kargs):
    #     form=self.form_class(request.POST)
    #     if form.is_valid():
    #         form.instance.user=request.user
    #         # add user feild
    #         form.save()
    #         messages.success(request,"todo added successfully")
    #         return redirect("index")
    #     messages.error(request,"failed to create todo")
    #     return render(request,self.template_name,{"form":form})

@method_decorator(signin_required,name="dispatch") 
class TaskListView(ListView):
    model=Tasl
    template_name="task-list.html"
    context_object_name="tasks"

    #we have to change query set
    def get_queryset(self) :
        return Tasl.objects.filter(user=self.request.user).order_by("-created_date")

    # def get(self,request,*args,**kargs):
    #     qs=Tasl.objects.filter(user=request.user)
    #     return render(request,self.template_name,{"tasks":qs})

@method_decorator(signin_required,name="dispatch")     
class TaskDetailView(DetailView):
    model=Tasl
    template_name="task-detail.html"
    context_object_name="task"

    # def get(self,request,*args,**kargs):
    #     id=kargs.get("pk")
    #     qs=Tasl.objects.get(id=id)
    #     return render(request,self.template_name,{"task":qs})

@method_decorator(signin_required,name="dispatch")     
class TaskEditView(UpdateView):
        model=Tasl
        form_class=TaskChangeForm
        template_name="task-edit.html"
        success_url=reverse_lazy("task-list")

        def form_valid(self, form):
            messages.success(self.request,"changed")
            return super().form_valid(form)

        # def get(self,request,*args,**kargs):
        #     id=kargs.get("pk")
        #     obj=Tasl.objects.get(id=id)
        #     form=self.form_class(instance=obj)
        #     return render(request,self.template_name,{"form":form})
        # def post(self,request,*args,**kargs):
        #     id=kargs.get("pk")
        #     obj=Tasl.objects.get(id=id)
        #     form=self.form_class(instance=obj,data=request.POST)
        #     if form.is_valid():
        #         form.save()
        #         messages.success(request,"todo changed successfully")
        #         return redirect("task-list")
        #     messages.error(request,"failed to update todo")
        #     return render(request,self.template_name,{"form":form})

@signin_required       
def task_delete_view(request,*args,**kargs):
    id=kargs.get("pk")
    Tasl.objects.get(id=id).delete()
    messages.success(request,"task removed")
    return redirect("task-list")

def sign_out_view(request,*args,**kargs):
    logout(request)
    return redirect("signin")

class PasswordResetView(FormView):
    model=User
    template_name="password-reset.html"
    form_class=PasswordResetForm

    # def get(self,request,*args,**kargs):
    #     form=self.form_class()
    #     return render(request,self.template_name,{"form":form})

    def post(self,request,*args,**kargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get("username")
            email=form.cleaned_data.get("email")
            pwd1=form.cleaned_data.get("password1")
            pwd2=form.cleaned_data.get("password2")

            if pwd1==pwd2:
                
                try:
                    usr=User.objects.get(username=username,email=email)
                    usr.set_password(pwd1)
                    usr.save()
                    messages.success(request,"password changed")
                    return redirect("signin")
                except Exception as e:
                    messages.error(request,"invalid credentials")
                    return render(request,self.template_name,{"form":form})
            else:
                messages.error(request,"password missmatch")
                return render(request,self.template_name,{"form":form})
                    


