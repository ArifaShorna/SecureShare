from django.shortcuts import render, redirect
from .forms import CustomUserRegisterForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import F
from .models import UploadedFile, ActivityLog, SharedFile
from .encryption import encrypt_file, decrypt_file, generate_hash
from django.db.models import F

def home(request):
    return render(request, 'home.html')


def register(request):
    form = CustomUserRegisterForm()

    if request.method == "POST":
        form = CustomUserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')

    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')

        if uploaded_file:
            file_data = uploaded_file.read()

            original_hash = generate_hash(file_data)
            encrypted_data = encrypt_file(file_data)

            uploaded = UploadedFile(
                user=request.user,
                file_hash=original_hash
            )

            uploaded.file.save(uploaded_file.name, ContentFile(encrypted_data))
            uploaded.save()

            messages.success(request, "File uploaded successfully!")

            ActivityLog.objects.create(
                user=request.user,
                action='Uploaded',
                file_name=uploaded_file.name
            )

            return redirect('dashboard')

    search_query = request.GET.get('search')

    if search_query:
        files = UploadedFile.objects.filter(
            user=request.user,
            file__icontains=search_query
        ).order_by('-uploaded_at')

        shared_files = SharedFile.objects.filter(
            shared_with=request.user,
            file__file__icontains=search_query
        ).select_related('file', 'shared_by').order_by('-shared_at')

        logs = ActivityLog.objects.filter(
            user=request.user,
            file_name__icontains=search_query
        ).order_by('-timestamp')

    else:
        files = UploadedFile.objects.filter(
            user=request.user
        ).order_by('-uploaded_at')

        shared_files = SharedFile.objects.filter(
            shared_with=request.user
        ).select_related('file', 'shared_by').order_by('-shared_at')

        logs = ActivityLog.objects.filter(
            user=request.user
        ).order_by('-timestamp')
        download_logs = ActivityLog.objects.filter(
            user=request.user,
            action='Downloaded'
        ).order_by('-timestamp')

    my_shared_files = SharedFile.objects.filter(
        shared_by=request.user
    ).select_related('file', 'shared_with').order_by('-shared_at')

    total_uploaded = UploadedFile.objects.filter(
        user=request.user
    ).count()

    total_shared = SharedFile.objects.filter(
        shared_with=request.user
    ).count()

    total_logs = ActivityLog.objects.filter(
        user=request.user
    ).count()

    own_downloads = sum(
        file.download_count for file in UploadedFile.objects.filter(user=request.user)
    )

    shared_downloads = sum(
        shared.file.download_count for shared in SharedFile.objects.filter(shared_with=request.user)
    )

    total_downloads = own_downloads + shared_downloads

    user_profile = request.user
    download_logs = ActivityLog.objects.filter(
        user=request.user,
        action='Downloaded'
    ).order_by('-timestamp')

    return render(request, 'dashboard.html', {
        'files': files,
        'logs': logs,
        'shared_files': shared_files,
        'my_shared_files': my_shared_files,
        'total_uploaded': total_uploaded,
        'total_shared': total_shared,
        'total_logs': total_logs,
        'total_downloads': total_downloads,
        'user_profile': user_profile,
        'download_logs': download_logs,
    })


def user_logout(request):
    logout(request)
    return redirect('login')





@login_required
def download_file(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)

        is_owner = uploaded_file.user == request.user
        is_shared = SharedFile.objects.filter(
            file=uploaded_file,
            shared_with=request.user
        ).exists()

        if not is_owner and not is_shared:
            return HttpResponse("You do not have permission to download this file.")

        with uploaded_file.file.open('rb') as f:
            encrypted_data = f.read()

        decrypted_data = decrypt_file(encrypted_data)

        current_hash = generate_hash(decrypted_data)

        if current_hash != uploaded_file.file_hash:
            return HttpResponse("Warning: File integrity check failed. File may be tampered.")

        # Download count update
        if uploaded_file.download_count is None:
            uploaded_file.download_count = 0

        uploaded_file.download_count += 1
        uploaded_file.save()

        print("Download count now:", uploaded_file.download_count)

        ActivityLog.objects.create(
            user=request.user,
            action='Downloaded',
            file_name=uploaded_file.file.name
        )

        response = HttpResponse(decrypted_data)
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.file.name}"'

        return response

    except UploadedFile.DoesNotExist:
        return HttpResponse("File not found.")



@login_required
def share_file(request, file_id):
    file_obj = UploadedFile.objects.get(id=file_id)

    if request.method == "POST":
        email = request.POST.get('email')

        try:
            shared_user = User.objects.get(email=email)

            SharedFile.objects.create(
                file=file_obj,
                shared_by=request.user,
                shared_with=shared_user
            )

            messages.success(request, "File shared successfully!")

        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")

    return redirect('dashboard')

@login_required
def delete_file(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id, user=request.user)

        file_name = uploaded_file.file.name

        uploaded_file.file.delete()
        uploaded_file.delete()

        ActivityLog.objects.create(
            user=request.user,
            action='Deleted',
            file_name=file_name
        )

        messages.success(request, "File deleted successfully!")

        return redirect('dashboard')

    except UploadedFile.DoesNotExist:
        return HttpResponse("File not found or you do not have permission to delete it.")
    



def unshare_file(request, share_id):
    shared = SharedFile.objects.get(id=share_id)

    if shared.shared_by == request.user:
        shared.delete()
        messages.success(request, "Access removed successfully!")

    return redirect('dashboard')



@login_required
def preview_file(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)

        is_owner = uploaded_file.user == request.user
        is_shared = SharedFile.objects.filter(
            file=uploaded_file,
            shared_with=request.user
        ).exists()

        if not is_owner and not is_shared:
            return HttpResponse("You do not have permission to preview this file.")

        with uploaded_file.file.open('rb') as f:
            encrypted_data = f.read()

        decrypted_data = decrypt_file(encrypted_data)

        current_hash = generate_hash(decrypted_data)

        if current_hash != uploaded_file.file_hash:
            return HttpResponse("Warning: File integrity check failed. File may be tampered.")

        import mimetypes

        file_type, _ = mimetypes.guess_type(uploaded_file.file.name)

        response = HttpResponse(
            decrypted_data,
            content_type=file_type or 'application/octet-stream'
        )

        response['Content-Disposition'] = f'inline; filename="{uploaded_file.file.name}"'
        return response

    except UploadedFile.DoesNotExist:
        return HttpResponse("File not found.")