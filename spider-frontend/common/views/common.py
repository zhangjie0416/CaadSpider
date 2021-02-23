from django.shortcuts import redirect


def login_required(view_func):
    '''调用视图函数之前需要先登录'''

    def wrapper(request, *view_args, **view_kwargs):
        # 判断是否存在islogin　session信息
        if request.session.get('islogin'):
            # 用户已登录
            return view_func(request, *view_args, **view_kwargs)
        else:
            # 用户没登录,则跳转到登录页面
            return redirect('/login.html')

    return wrapper
