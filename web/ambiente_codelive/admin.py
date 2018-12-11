import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib import admin

# Register your models here.
from .models import Perfil, Tag, NivelDeDificuldade, Desafio, CasoDeTeste, Resposta, HistoricoDesafio, \
    CorrecaoAutomaticaDeResposta, ResultadoDeCasoDeTesteDeCorrecaoAutomatica, ProxyDesafio, \
ProxyDesafioProfessor, ProxyRespostaProfessor, ProxyResposta, ProxyPerfil

from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from django.contrib.auth import get_permission_codename

from django.contrib.auth.models import User

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.urls import reverse

from django.utils.html import format_html

from django.contrib.auth.admin import Group

from .models import Desafio

from django.shortcuts import get_object_or_404


class CasoDeTesteInline(admin.TabularInline):
    model = CasoDeTeste
    extra = 0
    fields = ('entrada', 'saida', 'desafio')


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin): #dar uma olhada nisso
    change_form_template = 'resposta/resposta_admin_change_form.html'
    add_form_template = 'resposta/resposta_admin_add_form.html'
    change_list_template = 'resposta/resposta_admin_change_list.html'
    search_fields = ('desafio',)
    list_per_page = 20
    list_display = ('desafio','usuario', 'data_da_resposta')
    list_display_links = list_display
    list_filter = ('desafio',)
    ordering = ('-data_da_resposta',)
    actions = ('avaliar_resposta',)
    readonly_fields = ['data_da_resposta','desafio'] #pra não mostrar a edição

    fieldsets = [
        (None,               {'fields': ['resposta_do_desafio']}),
        (None, {'fields':['desafio','data_da_resposta']}),
    ]


    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.groups.filter(name='Estudantes').exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']
            if 'avaliar_resposta' in actions:
                del actions['avaliar_resposta']
        return actions


    def save_model(self, request, obj, form, change):
        
        usuario = User.objects.get(id=request.user.id)
                
        obj.usuario = usuario
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
            
        if request.user.groups.filter(name='Professores'):
        	return qs.filter(desafio__autor=request.user.id)

        if request.user.groups.filter(name='Estudantes').exists():
            autor = request.user.id
            return Resposta.objects.filter(usuario=autor)

    def changeform_view(self, request, object_id=None,form_url='',extra_context=None):
        if object_id is not None:
            extra_context = extra_context or {}
            extra_context['correcoes'] = CorrecaoAutomaticaDeResposta.objects.filter(resposta=object_id)
        return super().changeform_view(request,object_id,form_url,extra_context)


    def avaliar_resposta(self, request, queryset):
        base_dir_real = settings.LOCAL_PROJECT_ROOT
        # build da maquina python
        python_machine_path = Path(settings.VM_PYTHON_ROOT)
        #subprocess.Popen('cd {} && docker-compose build'.format(python_machine_path), shell=True).wait()
        python_machine_image_name = 'python_codelive_vm_python'
        conta_respostas = 0
        for resposta in queryset:
            correcao = CorrecaoAutomaticaDeResposta.objects.create(resposta=resposta)
            conta_respostas += 1
            total_score = 0.0
            total_cpu = 0.0
            total_runtime = 0.0
            total_memory_kb = 0.0
            total_memory_pc = 0.0

            millis = int(round(time.time() * 1000))
            total_score = 0.0
            tmpdir_path = Path(os.path.join(settings.BASE_DIR, 'tmp'))
            resposta_tmpdir_path = tmpdir_path / str(millis)
            resposta_tmpdir_path.mkdir()
            resposta_tmpfile_path = resposta_tmpdir_path / 'resposta.py'
            with open(resposta_tmpfile_path, 'w+', encoding='utf-8') as f:
                # f.write(resposta.resposta_do_desafio.replace('\r\n', '\n')) # no windows, usar replace
                f.write(resposta.resposta_do_desafio)
            for testcase in CasoDeTeste.objects.filter(desafio=resposta.desafio).all():
                testcase_tmpdir_path = resposta_tmpdir_path / 'testcase-{}'.format(testcase.pk)
                testcase_tmpdir_path.mkdir()
                # copia os arquivos de resposta e entrada para a pasta do testcase
                shutil.copy(resposta_tmpfile_path, testcase_tmpdir_path)
                testcase_tmpfile_path = testcase_tmpdir_path / 'entrada.txt'
                testcase_tmpdir_path_real = str(testcase_tmpdir_path).replace(settings.BASE_DIR, base_dir_real)
                results_file_path = testcase_tmpdir_path / 'results.json'
                with open(testcase_tmpfile_path, 'w+', encoding='utf-8') as f:
                    # f.write(testcase.entrada.replace('\r\n', '\n')) # no windows, usar replace
                    f.write(testcase.entrada)
                proc = subprocess.Popen(
                    'cd {} && docker run --memory 32M --cpus 0.1 -v {}:/usr/src/app --rm {} python -c \"import psutil;'
                    'import time;import json;'
                    'start = time.time();'
                    'total_memory = psutil.virtual_memory().total;used_memory = psutil.virtual_memory().used;'
                    'used_cpu = psutil.cpu_times().user;'
                    'import {};'
                    'end = time.time();total_time = end-start;'
                    'used_memory = psutil.virtual_memory().used - used_memory;used_cpu = psutil.cpu_times().user - used_cpu;'
                    'results = {{ \'runtime\': total_time, \'cpu\': used_cpu, \'memory_kb\': (used_memory / 1024),'
                    '\'memory_pc\': (used_memory / total_memory) }}; f = open(\'results.json\', \'w\');'
                    'json.dump(results, f); f.close()\" {}'.format(
                        resposta_tmpdir_path, testcase_tmpdir_path_real, python_machine_image_name,
                        'resposta', 'entrada.txt'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                std, err = proc.communicate()
                rc = proc.wait()

                resultado_caso_de_teste = ResultadoDeCasoDeTesteDeCorrecaoAutomatica(correcao=correcao)
                if std:
                    resultado_caso_de_teste.saida_padrao = std.decode()
                if err:
                    resultado_caso_de_teste.saida_erro = err.decode()

                if results_file_path.exists():
                    with open(results_file_path, 'r') as r:
                        results = json.load(r)
                        resultado_caso_de_teste.total_runtime = results['runtime']
                        resultado_caso_de_teste.total_cpu = results['cpu']
                        resultado_caso_de_teste.total_memoria_kb = results['memory_kb']

                        total_runtime += results['runtime']
                        total_cpu += results['cpu']
                        total_memory_kb += results['memory_kb']
                        total_memory_pc += results['memory_pc']

                if str(std.decode()).strip() == testcase.saida:
                    total_score += 1.0
                    resultado_caso_de_teste.pontuacao = 1.0
                else:
                    resultado_caso_de_teste.pontuacao = 0.0
                resultado_caso_de_teste.save()

            # remover a linha a seguir quando não quiser ver os arquivos de saída
            # shutil.rmtree(resposta_tmpdir_path, ignore_errors=True)

            testcase_count = CasoDeTeste.objects.filter(desafio=resposta.desafio).count()
            correcao.pontuacao = total_score / testcase_count
            correcao.total_runtime = total_runtime / testcase_count
            correcao.total_cpu = total_cpu / testcase_count
            correcao.total_memoria_kb = total_memory_kb / testcase_count
            correcao.save()
        self.message_user(request, '{} resposta(s) corrigida(s)'.format(conta_respostas))

    avaliar_resposta.short_description = 'Corrigir respostas selecionadas'

class ProxyRespostaProfessorInline(admin.TabularInline):
    model = ProxyRespostaProfessor
    extra = 0
    fields = ('resposta_do_desafio',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Professores').exists():
            return qs
        return qs.filter(usuario=request.user)

    

@admin.register(ProxyDesafioProfessor) #retorna a lista de desafios cadastrados pelos professores para o aluno
class ProxyDesafioProfessorAdmin(admin.ModelAdmin):
    change_form_template = 'desafio/desafio_admin_change_form.html'
    change_list_template = 'desafio/desafio_admin_change_list.html'    
    search_fields = ('titulo', 'enunciado',)
    list_per_page = 20
    list_display = ('titulo', 'autor', 'enunciado','nivel_de_dificuldade',)
    list_display_links = list_display
    list_filter = ('titulo', 'enunciado', )
    ordering = ('-data_de_cadastro',)
    inlines = [ProxyRespostaProfessorInline,]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.usuario = request.user
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        qs = super().get_queryset(request)  
         #preciso retornar só os desafios do usuario que está no grupo -> OK ESTÁ RETORNANDO
        if request.user.groups.filter(name='Estudantes').exists() and qs.filter(estah_publicado=True):
            usuarios_grupo = Group.objects.get(name="Professores").user_set.all()
            return qs.filter(autor__in=usuarios_grupo, estah_publicado=True)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id and not request.user.groups.filter(name='Professores').exists():
            extra_context['show_save_as_new'] = False
            extra_context['show_save'] = True
            extra_context['show_save_and_continue'] = False
            extra_context['show_delete'] = False
            extra_context['show_save_and_add_another'] = False

        return super(ProxyDesafioProfessorAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Título',               {'fields': ['titulo']}),
        (None, {'fields': ['tags']}),
        ('Enunciado e Descrição', {'fields': ['enunciado','descricao']}),
        ('Pré-Código', {'fields': ['pre_codigo']}),
        ('Nível de Dificuldade', {'fields': ['nivel_de_dificuldade']}),
        (None, {'fields': ['estah_publicado']}),
        ('Anexar Arquivo',{'fields':['arquivo']}),
    ]
    search_fields = ('titulo', 'descricao',)
    list_per_page = 20
    list_display = ('titulo', 'descricao','enunciado',)
    list_display_links = list_display
    list_filter = ('titulo',)
    ordering = ('-data_de_cadastro',)
    inlines = (CasoDeTesteInline,)

    def save_model(self, request, obj, form, change):
        usuario = User.objects.get(id=request.user.id)  
        obj.autor = usuario
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name='Professores').exists():
            return qs.filter(autor=request.user.id)
         

@admin.register(ResultadoDeCasoDeTesteDeCorrecaoAutomatica)
class ResultadoDeCasoDeTesteDeCorrecaoAutomaticaAdmin(admin.ModelAdmin):
    #change_form_template = 'resultado/resultado_admin_change_form.html'
    #add_form_template = 'resultado/resultado_admin_add_form.html'
    #change_list_template = 'resultado/resultado_admin_change_list.html'
    search_fields = ('pontuacao',)
    list_per_page = 20
    list_display = ('correcao', 'pontuacao',)   
    list_display_links = list_display
    list_filter = ('pontuacao', )
    

@admin.register(CorrecaoAutomaticaDeResposta)
class CorrecaoAutomaticaDeRespostaAdmin(admin.ModelAdmin):
    change_form_template = 'correcao/correcao_admin_change_form.html'
   # add_form_template = 'correcao/correcao_admin_add_form.html'
    change_list_template = 'correcao/correcao_admin_change_list.html'

    def changeform_view(self, request, object_id=None,form_url='',extra_context=None):
        if object_id is not None:
            extra_context = extra_context or {}
            extra_context['resultados'] = ResultadoDeCasoDeTesteDeCorrecaoAutomatica.objects.filter(correcao=object_id)
        return super().changeform_view(request,object_id,form_url,extra_context)






# configurar o admin
admin.site.register(Tag)
admin.site.register(NivelDeDificuldade)
admin.site.register(CasoDeTeste)

