from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Organization, CustomUser, Role
from django.http import HttpResponseForbidden
from .forms import OrganizationForm
from django.contrib import messages


@login_required
def user_dashboard(request):
    user = request.user
    
    if user.is_superuser:
        organizations = Organization.objects.filter(is_main=False)  # Exclude the main organization
        return render(request, 'orgs/superuser_dashboard.html', {'organizations': organizations})
    
    elif user.is_org_admin:
        users = CustomUser.objects.filter(organization=user.organization, is_org_admin=False)
        return render(request, 'orgs/org_admin_dashboard.html', {'users': users})
    
    elif user.organization:
        return render(request, 'orgs/user_dashboard.html', {'organization': user.organization})
    
    return redirect('logout')


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
        else:
            return render(request, 'orgs/login.html', {'error': 'Invalid credentials'})
    return render(request, 'orgs/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def manage_organization(request, org_id=None):
    """
    Handles both adding a new organization and updating an existing one.
    Allows setting or updating the organization admin during creation or update.
    """
    is_update = org_id is not None
    organization = None
    org_admin_user = None

    # If updating, get the organization object
    if is_update:
        organization = get_object_or_404(Organization, id=org_id)
        org_admin_user = organization.users.filter(is_org_admin=True).first()

    if request.method == 'POST':
        org_form = OrganizationForm(request.POST, instance=organization)
        
        # Capture organization admin details
        admin_name = request.POST.get('admin_name')
        admin_username = request.POST.get('admin_username')
        admin_email = request.POST.get('admin_email')
        admin_password = request.POST.get('admin_password')
        
        if org_form.is_valid():
            # Save or update the organization details
            org = org_form.save()

            # Handle org admin creation or update
            if is_update and org_admin_user:
                # If updating, update the existing admin details
                org_admin_user.username = admin_username
                org_admin_user.email = admin_email
                org_admin_user.set_password(admin_password)
                org_admin_user.save()
            else:
                # If adding a new org, create a new admin user (CustomUser model)
                org_admin_user = CustomUser.objects.create_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    first_name=admin_name,
                )
                org_admin_user.is_org_admin = True
                org_admin_user.save()

            # Assign org admin user to the organization
            org_admin_user.organization = org
            org_admin_user.save()

            # Redirect after successful creation or update
            return redirect('user_dashboard')

    else:
        # If GET request, load the existing org data or initialize an empty form
        org_form = OrganizationForm(instance=organization)
        if org_admin_user:
            admin_name = org_admin_user.first_name
            admin_username = org_admin_user.username
            admin_email = org_admin_user.email
        else:
            admin_name = admin_username = admin_email = ''

    return render(request, 'orgs/add_update_org.html', {
        'form': org_form,
        'organization': organization,
        'is_update': is_update,
        'admin_name': admin_name,
        'admin_username': admin_username,
        'admin_email': admin_email,
    })

@login_required
def delete_organization(request, org_id):
    """
    Deletes an organization if the logged-in user is a superuser.
    A confirmation page is shown before deletion.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to delete organizations.")
    
    organization = get_object_or_404(Organization, id=org_id)
    organization.delete()
    return redirect('user_dashboard')  # Redirect to dashboard after deletion

@login_required
def add_role(request):
    """
    Allows an organization admin to create roles for their organization.
    """
    if not request.user.is_org_admin:
        messages.error(request, "You are not authorized to add roles.")
        return redirect("user_dashboard")

    if request.method == "POST":
        role_name = request.POST.get("role_name")
        role_description = request.POST.get("role_description")
        
        if role_name:
            Role.objects.create(
                name=role_name,
                description=role_description,
                organization=request.user.organization,
            )
            messages.success(request, "Role added successfully!")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Role name is required.")

    return render(request, "orgs/add_role.html")


@login_required
def add_update_user(request, user_id=None):
    """
    Allows an organization admin to add or update users within their organization.
    """
    if not request.user.is_org_admin:
        messages.error(request, "You are not authorized to manage users.")
        return redirect("org_admin_dashboard")

    user = None
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id, organization=request.user.organization)

    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role_id = request.POST.get("role")
        role = get_object_or_404(Role, id=role_id, organization=request.user.organization)

        if user:
            # Update user
            user.first_name = name
            user.username = username
            user.email = email
            user.role = role
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, "User updated successfully!")
        else:
            # Add new user
            CustomUser.objects.create_user(
                first_name=name,
                username=username,
                email=email,
                password=password,
                role=role,
                organization=request.user.organization,
            )
            messages.success(request, "User added successfully!")
        return redirect("user_dashboard")

    roles = Role.objects.filter(organization=request.user.organization)
    return render(request, "orgs/add_update_user.html", {"user": user, "roles": roles})


@login_required
def delete_user(request, user_id):
    """
    Deletes a user in the same organization as the logged-in admin.
    """
    if not request.user.is_org_admin:
        messages.error(request, "You are not authorized to delete users.")
        return redirect("user_dashboard")

    user = get_object_or_404(CustomUser, id=user_id, organization=request.user.organization)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect("user_dashboard")
