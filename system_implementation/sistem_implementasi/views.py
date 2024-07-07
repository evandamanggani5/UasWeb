from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from .models import SistemCerdas, PickleFile, CSVFile
from .forms import PickleFileForm, CSVFileForm
import requests
import pickle
import csv
import os

def home(request):
    api_url = 'http://172.16.1.130:8001/training-testing-results/'
    response = requests.get(api_url)
    api_projects = []
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            api_projects = data
            print('ini isi api: ', api_projects)

            # Simpan data ke database lokal
            for project in api_projects:
                project_name = project.get('project')
                training_result = project.get('training_result')
                if project_name and training_result:
                    obj, created = SistemCerdas.objects.update_or_create(
                        nama_sistem_cerdas=project_name,
                        defaults={'file_sistem_cerdas': training_result}
                    )
                    if created:
                        print(f"Created new entry: {obj}")
                    else:
                        print(f"Updated entry: {obj}")

    local_projects = SistemCerdas.objects.all()
    for local_project in local_projects:
        print('ini isi local: ', local_project.file_sistem_cerdas)
    
    if request.method == 'POST':
        if 'upload_pickle' in request.POST:
            print('Upload Pickle Detected')
            form_pickle = PickleFileForm(request.POST, request.FILES)
            if form_pickle.is_valid():
                form_pickle.save()
                return JsonResponse({'message': 'Pickle file uploaded successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Failed to upload pickle file'}, status=400)
        elif 'upload_csv' in request.POST:
            print('Upload CSV Detected')
            form_csv = CSVFileForm(request.POST, request.FILES)
            if form_csv.is_valid():
                form_csv.save()
                return JsonResponse({'message': 'CSV file uploaded successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Failed to upload CSV file'}, status=400)
    
    form_pickle = PickleFileForm()
    form_csv = CSVFileForm()

    pickles = PickleFile.objects.all()
    csv_files = CSVFile.objects.all()
    print('ini isi pickles: ', pickles)
    print('ini isi csv_files: ', csv_files)
    accuracy = None
    test_results = None
    csv_data = None

    if 'load_pickle' in request.GET:
        pickle_id = request.GET.get('load_pickle')
        try:
            pickle_file = PickleFile.objects.get(pk=pickle_id)
            file_path = pickle_file.file.path
            print(f"Memuat file pickle dari path: {file_path}")

            if not os.path.exists(file_path):
                print(f"File tidak ditemukan: {file_path}")
                raise Http404("File tidak ditemukan atau format tidak valid")

            with open(file_path, 'rb') as f:
                results = pickle.load(f)

            accuracy = results.get('accuracy')
            y_test = results.get('y_test')
            y_pred = results.get('y_pred')

            test_results = list(zip(y_test, y_pred))
            return JsonResponse({'accuracy': accuracy, 'test_results': test_results}, status=200)
        except (PickleFile.DoesNotExist, KeyError, pickle.UnpicklingError, AttributeError) as e:
            print(f"Error saat memuat file pickle: {e}")
            return JsonResponse({'message': 'Failed to load pickle file'}, status=400)
    
    if 'load_csv' in request.GET:
        csv_id = request.GET.get('load_csv')
        try:
            csv_file = CSVFile.objects.get(pk=csv_id)
            file_path = csv_file.file.path
            print(f"Memuat file CSV dari path: {file_path}")

            if not os.path.exists(file_path):
                print(f"File tidak ditemukan: {file_path}")
                raise Http404("File CSV tidak ditemukan atau format tidak valid")

            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                csv_data = list(reader)
            return JsonResponse({'csv_data': csv_data}, status=200)
        except (CSVFile.DoesNotExist, IOError) as e:
            print(f"Error saat memuat file CSV: {e}")
            return JsonResponse({'message': 'Failed to load CSV file'}, status=400)
    
    query = request.GET.get('q', '')
    print("Query:", query)  # Debug print
    filtered_api_projects = []
    filtered_local_projects = []
    if query:
        filtered_api_projects = [project for project in api_projects if query.lower() in project['project'].lower()]
        filtered_local_projects = SistemCerdas.objects.filter(nama_sistem_cerdas__icontains=query)
        for local_project in filtered_local_projects:
            if local_project.file_sistem_cerdas.endswith(".csv"):
                local_project.file_format = "CSV"
            elif local_project.file_sistem_cerdas.endswith(".pkl") or local_project.file_sistem_cerdas.endswith(".pickle"):
                local_project.file_format = "Pickle"
            else:
                local_project.file_format = "Unknown"
        print("Filtered local projects:", filtered_local_projects)  # Debug print
        for project in filtered_local_projects:
            print(project.nama_sistem_cerdas)  # Debug print each project name
        return JsonResponse({
            'filtered_api_projects': [project for project in filtered_api_projects],
            'filtered_local_projects': [
                {
                    'nama_sistem_cerdas': project.nama_sistem_cerdas,
                    'file_sistem_cerdas': project.file_sistem_cerdas,
                    'file_format': getattr(project, 'file_format', 'Unknown')
                } for project in filtered_local_projects
            ]
        }, status=200)
    else:
        filtered_api_projects = api_projects
        filtered_local_projects = local_projects

    context = {
        'api_projects': api_projects,
        'local_projects': local_projects,
        'form_pickle': form_pickle,
        'form_csv': form_csv,
        'pickles': pickles,
        'csv_files': csv_files,
        'accuracy': accuracy,
        'test_results': test_results,
        'csv_data': csv_data,
        'filtered_api_projects': filtered_api_projects,
        'filtered_local_projects': filtered_local_projects,
        'query': query,
    }
    return render(request, 'home.html', context)

def download_file(request, file_id):
    sistem_cerdas = get_object_or_404(SistemCerdas, id=file_id)
    file_url = sistem_cerdas.file_sistem_cerdas  # Ambil URL langsung dari model tanpa mengencode ulang

    print('Mengakses URL:', file_url)  # Log untuk memastikan URL benar

    try:
        response = requests.get(file_url)
        response.raise_for_status()
        print("Download Detected")
    except requests.exceptions.RequestException as e:
        print(f'Error saat mengakses file: {e}')  # Log kesalahan
        raise Http404("File tidak ditemukan di server eksternal")

    # Tentukan folder penyimpanan untuk file CSV atau Pickle
    if file_url.endswith('.csv'):
        filename = file_url.split('/')[-1]
        folder_path = 'csvs'
    elif file_url.endswith('.pkl') or file_url.endswith('.pickle'):
        filename = file_url.split('/')[-1]
        folder_path = 'pickles'
    else:
        raise Http404("Tipe file tidak didukung")

    path = os.path.join(folder_path, filename)
    
    # Buat folder jika belum ada
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Simpan file ke folder yang sesuai
    with open(path, 'wb') as file:
        file.write(response.content)

    # Mengatur response untuk pengunduhan file
    if file_url.endswith('.csv'):
        response_content = HttpResponse(response.content, content_type='text/csv')
        response_content['Content-Disposition'] = f'attachment; filename="{filename}"'
    elif file_url.endswith('.pkl') or file_url.endswith('.pickle'):
        response_content = HttpResponse(response.content, content_type='application/octet-stream')
        response_content['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response_content