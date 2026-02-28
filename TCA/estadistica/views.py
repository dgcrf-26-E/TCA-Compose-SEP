from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from usuarios.models import Registro, Acciones, Notificacion, Area, Rubro, UsuarioP, Periodo
from django.db.models import Count, Q, Avg, IntegerField
from django.db.models.functions import ExtractYear, Substr
from django.http import HttpResponse
import openpyxl as opxl

@login_required
def opc_periodo(request):
    if request.method == 'GET':
        context = {
            'periodo_form': Periodo.objects.all()
        }
        return render(request, "estadistica/periodo.html", context)
    else:
        return render(request, "base/error404.html")

@login_required
def general(request):
    if request.method == 'POST':
        
        opc = [str(a.pk) for a in Periodo.objects.all() ]

        seleccion = str(request.POST.get('periodo'))

        if (seleccion not in opc) and (seleccion != 'all'):
            return render(request, "base/error404.html")

        userDataI = UsuarioP.objects.filter(user__username=request.user).first()
        
        registros = Registro.objects.filter(area=userDataI.OR)
        if seleccion in opc:
            registros = Registro.objects.filter(area=userDataI.OR, periodo__id=int(seleccion))

        if userDataI.tipo == "1":
            registros = Registro.objects.all()
            if seleccion in opc:
                registros = Registro.objects.filter(periodo__id=int(seleccion))
        
        consultarAreas = Area.objects.all()
        consultarRubros = Rubro.objects.all()

        # nombres_areas = [area.nickname for area in consultarAreas]
        # # lista_años = [str(año) for año in range(2020, datetime.now().year + 1)]
        # lista_años = range(2020, datetime.now().year + 1)

        # registros_OR = registros.values('area').annotate(total= Count('idRegistro'))
        # registros_OR_year = registros.values('area', year=ExtractYear('fecha_inicio')).annotate(total= Count('idRegistro')).order_by('area', 'year')

        # for registro in registros_OR:
        #     print(f"{consultarAreas.filter(idArea=registro['area']).first().name}  TOTAL {registro['total']}")

        # for registro in registros_OR_year:
        #     print(f"Área: {consultarAreas.filter(idArea=registro['area']).first().name}, Año: {registro['year']}, Total registros: {registro['total']}")
        
        registro_V_A = []
        visitasT = 0
        acuerdosT = 0
        pendientesT = 0
        atenditosT = 0


        #Tabla 1
        # registros_visitas = registros.values('area', 'fecha_inicio').annotate(total= Count('idRegistro'), ).order_by('area', 'fecha_inicio')
        registros_visitas = registros.values('area', 'fecha_inicio').annotate(
            total=Count('idRegistro'),
            pendiente=Count('idRegistro', filter=Q(estado="1")),
            atendido=Count('idRegistro', filter=Q(estado="2")),
            seguimiento = Avg('porcentaje_avance', output_field=IntegerField())
        ).order_by('area', 'fecha_inicio')

        ors_mapa = { area_.name.replace("OR ",""): [] for area_ in consultarAreas[:32]}

        for registro in registros_visitas:
            oficina_ = str(consultarAreas.filter(idArea=registro['area']).first().name).replace("OR ","")
            if oficina_ in ors_mapa:
                ors_mapa[oficina_].append({
                    'fecha': datetime.strftime(registro['fecha_inicio'], "%d/%m/%Y"),
                    'total': registro['total'],
                    'pendiente': registro['pendiente'],
                    'atendido': registro['atendido'],
                    'avance': registro['seguimiento'],
                    })
        
        # print(ors_mapa)

        for registro in registros_visitas:
            # print(f"OR: {consultarAreas.filter(idArea=registro['area']).first().name} Fecha: {registro['fecha_inicio']} TOTAL {registro['total']}")
            registro_V_A.append({
                'area': str(consultarAreas.filter(idArea=registro['area']).first().name).replace("OR ",""),
                'fecha': datetime.strftime(registro['fecha_inicio'], "%d/%m/%Y"),
                'total': registro['total'],
                'pendiente': registro['pendiente'],
                'atendido': registro['atendido'],
            })

        # registros_years = registros.values( "fecha_inicio", year=ExtractYear('fecha_inicio')).annotate(
        #tabla 2
        registros_years = registros.values(year=ExtractYear('fecha_inicio')).annotate(
            total_registros=Count('idRegistro'),
            total_fechas_unicas=Count(Substr('claveAcuerdo', 4), distinct=True),
            total_pendi=Count('idRegistro', filter=Q(estado="1")), 
            total_aten=Count('idRegistro', filter=Q(estado="2")), 
            ).order_by('year')
        

        #tabla 3
        registros_rubros = (registros.values("rubro", year=ExtractYear('fecha_inicio'))
             .annotate(total_unico=Count('rubro'))
             .order_by("rubro", 'year'))
        # registros_rubros = registros.values( "rubro",year=ExtractYear('fecha_inicio')).annotate(
        #     total_unico=Count('rubro'),
        #     ).order_by("rubro",'year')

        col_años= [info['year'] for info in registros_years]

        data_by_rubro = {}
        for registro in registros_rubros:
            # rubro = registro['rubro']
            rubro = consultarRubros.filter(idRubro=registro["rubro"]).first().tipo
            yearT = registro['year']
            total = registro['total_unico']
            
            if rubro not in data_by_rubro:
                # data_by_rubro[rubro] = {year: 0 for year in lista_años}
                data_by_rubro[rubro] = {year: 0 for year in col_años}
            
            # Actualizar el año con el total correcto
            data_by_rubro[rubro][yearT] = total

        # print(data_by_rubro)

        # for registro in registros_rubros:
        #     print(f"Año: {registro["year"]}, Rubro: {consultarRubros.filter(idRubro=registro["rubro"]).first().tipo }, Acuerdos: {registro["total_unico"]}")

        for registro in registros_years:
            visitasT += registro['total_fechas_unicas']
            acuerdosT += registro['total_registros']
            pendientesT += registro['total_pendi']
            atenditosT += registro['total_aten']
        
        context = {
            "tabla1" : registro_V_A,
            "tabla2" : registros_years,
            "tabla3" : data_by_rubro,
            "visitas": len(registro_V_A),
            "acuerdos": acuerdosT,
            # "years": lista_años,
            "years": col_años,
            "seleccion": seleccion,
            "usuario": userDataI,
            "mapa": ors_mapa,
        }

        return render(request, "estadistica/informacion.html", context)
    
    else:
        return render(request, "base/error404.html")

@login_required
def pendientes(request):
    if(request.method == "GET"):

        opc = [str(a.pk) for a in Periodo.objects.all() ]
        userDataI = UsuarioP.objects.filter(user__username=request.user).first()

        registros = Registro.objects.filter(area=userDataI.OR, estado="1").order_by('fecha_inicio')
        # registros = Registro.objects.filter(area=userDataI.OR)
        if userDataI.tipo == "1":
            registros = Registro.objects.filter(estado="1").order_by('fecha_inicio')
            # registros = Registro.objects.all()

        # if userDataI.tipo == "1":
        #     registros = Registro.objects.all()
        
        workbook = opxl.Workbook()
        worksheet = workbook.active
            
        for valor in registros:

            oficina = valor.claveAcuerdo.split("/")
            fecha = valor.fecha_inicio.strftime("%Y")
            clave = valor.claveAcuerdo
            rubro = (valor.rubro.first()).tipo
            hallazgo = (valor.accionR.first()).antecedente
            descripcion = (valor.accionR.first()).descripcion
            avance = valor.porcentaje_avance

            areas1 = ", ".join([area.nickname for area in (valor.accionR.first()).area2.all()])

            # areal = ", ".join([area.nickname for area in valor.accionR])

            # print(f"OR:{oficina[1]} -- {fecha} -- CLAVE:{clave} -- {rubro[:5]} -- {descripcion} -- {avance}")
            worksheet.append([oficina[1], fecha, clave, rubro, hallazgo, descripcion, avance, areas1])
        
        worksheet.append(['Numero de Acuerdos Pendientes: ', registros.count()])

        response = HttpResponse(content = opxl.writer.excel.save_virtual_workbook(workbook), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename= "Acuerdos_Pendientes_a_{fecha1}.xlsx"'.format(fecha1 = date.today())

        return response

        # redirect("estadistica_p")
    
    else:
        return render(request, "base/error404.html")