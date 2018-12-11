import json

from django import template
from django.template.context import Context
from django.contrib.admin.templatetags.admin_modify import submit_row as admin_submit_row


register = template.Library()

@register.inclusion_tag('', takes_context=True)
def submit_row(context):
    return admin_submit_row(context)


@register.inclusion_tag('desafio/desafio_change.html', takes_context=True)
def desafio_change(context):
    desafio = context['original']
    context.update({
        'desafio': desafio
    })
    return context

@register.inclusion_tag('desafio-professor/desafio_professor_change.html', takes_context=True)
def desafio_professor_change(context):
    desafio = context['original']
    context.update({
        'desafio': desafio
    })
    return context

@register.inclusion_tag('resposta/resposta_change.html', takes_context=True)
def resposta_change(context):
    resposta = context['original']
    context.update({
        'resposta': resposta
    })
    return context


@register.inclusion_tag('resultado/resultado_change.html', takes_context=True)
def resultado_change(context):
    resultado = context['original']
    context.update({
        'resultado': resultado
    })
    return context

@register.inclusion_tag('correcao/correcao_change.html', takes_context=True)
def correcao_change(context):
    correcao = context['original']
    context.update({
        'correcao': correcao
    })
    return context

@register.inclusion_tag('admin/perfil_change.html', takes_context=True)
def perfil_change(context):
    perfil = context['original']
    context.update({
        'perfil': perfil
    })
    return context







