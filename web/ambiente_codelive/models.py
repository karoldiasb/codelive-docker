from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

#criar um model perfil e associar a um usuario
#ver um unico perfil
#tirar a imagem

class Perfil(models.Model):
    imagem  = models.FileField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

class ProxyPerfil(Perfil):
    class Meta:
        verbose_name = 'Meu Perfil'
        verbose_name_plural = 'Meus Perfis'
        proxy = True

class Tag(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    nome_das_tags = models.TextField('Nome da tag',blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.nome_das_tags)

class NivelDeDificuldade(models.Model):
    class Meta:
        verbose_name = 'Nível de dificuldade'
        verbose_name_plural = 'Níveis de Dificuldade'
    nivel = models.IntegerField('Nível de dificuldade')

    def __str__(self):
        return '{}'.format(self.nivel)

class Desafio(models.Model):
    class Meta:
        verbose_name = 'Desafio'
        verbose_name_plural = 'Desafios'
    titulo = models.CharField('Título do desafio',max_length=256)
    tags = models.ManyToManyField(Tag, verbose_name="Lista das tags")
    descricao = models.TextField('Descrição',blank=True, null=True) # TextField
    enunciado = models.TextField('Enunciado',blank=True, null=True)
    pre_codigo = models.TextField('Pré-código',blank=True, null=True) 
    estah_publicado = models.BooleanField('Está publicado',default='0') # estah_publicado; BolleanField
    autor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,default='0')
    nivel_de_dificuldade = models.ForeignKey('NivelDeDificuldade',on_delete=models.CASCADE)
    data_de_cadastro = models.DateTimeField('Data de Cadastro',auto_now_add=True) #data_de_cadastro; auto_now=True; add_now=True
    arquivo = models.FileField(null=True,blank=True)

    @property
    def respostas(self):
        return Resposta.objects.filter(acao=self)

    def __str__(self):
        return self.titulo

class ProxyDesafio(Desafio):
    class Meta:
        verbose_name = 'Meu Desafio'
        verbose_name_plural = 'Meus Desafios'
        proxy = True

class ProxyDesafioProfessor(Desafio):
    class Meta:
        verbose_name = 'Desafio Cadastrado'
        verbose_name_plural = 'Desafios Cadastrados'
        proxy = True
    
class CasoDeTeste(models.Model):
    class Meta:
        verbose_name = 'Caso de Teste'
        verbose_name_plural = 'Casos de Teste'
    entrada = models.TextField('Entrada',blank=True, null=True)
    saida = models.TextField('Saída',blank=True, null=True)
    desafio = models.ForeignKey('Desafio',on_delete=models.CASCADE)

    def __str__(self):
        return self.entrada + self.saida

class Resposta(models.Model):
    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'
    resposta_do_desafio = models.TextField('Resposta do desafio',blank=True, null=True)
    desafio = models.ForeignKey('Desafio',on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, default='0')
    data_da_resposta = models.DateTimeField('Data da Resposta',auto_now_add=True)

    def __str__(self):
        return ""

class ProxyResposta(Resposta):
    class Meta:
        verbose_name = 'Minha resposta'
        verbose_name_plural = 'Minhas respostas'
        proxy = True

class ProxyRespostaProfessor(Resposta):
    class Meta:
        verbose_name = 'Resposta do Professor'
        verbose_name_plural = 'Responder os Desafios do Professor'
        proxy = True

class HistoricoDesafio(models.Model):
    resposta = models.ForeignKey('Resposta',on_delete=models.CASCADE)
    #desafio_vencido = models.BolleanField(default=False) #boolean
    historico_do_desafio = models.BooleanField(default=True)
    #guardar a data

    def __str__(self):
        return self.historico_do_desafio


class CorrecaoAutomaticaDeResposta(models.Model):
    class Meta:
        verbose_name = 'Correção Automática de Resposta'
        verbose_name_plural = 'Correções automáticas de respostas'

    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE, related_name='correcoes')
    data_de_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    pontuacao = models.FloatField('Pontuação', default=0.0)
    total_cpu = models.FloatField('Uso de CPU (%)', null=True, blank=True)
    total_memoria_kb = models.FloatField('Uso de RAM (KB)', null=True, blank=True)
    total_runtime = models.FloatField('Tempo de execução (ms)', null=True, blank=True)

    def __str__(self):
        return str(self.data_de_criacao)


class ResultadoDeCasoDeTesteDeCorrecaoAutomatica(models.Model):
    class Meta:
        verbose_name = 'Resultado de caso de teste de correção automática'
        verbose_name_plural = 'Resultados de casos de teste de correções automáticas'

    correcao = models.ForeignKey(CorrecaoAutomaticaDeResposta, on_delete=models.CASCADE, related_name='resultados_casos_de_teste')
    data_de_criacao = models.DateTimeField('Criado em', auto_now_add=True)
    pontuacao = models.FloatField('Pontuação', default=0.0)
    total_cpu = models.FloatField('Uso de CPU (%)', null=True, blank=True)
    total_memoria_kb = models.FloatField('Uso de RAM (KB)', null=True, blank=True)
    total_runtime = models.FloatField('Tempo de execução (ms)', null=True, blank=True)
    saida_padrao = models.TextField('Saída padrão', null=True, blank=True)
    saida_erro = models.TextField('Saida erro', null=True, blank=True)

    def __str__(self):
        return str(self.data_de_criacao)

