import arcpy
from arcpy import *
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
x = arcpy.GetParameterAsText(0)
c = str(arcpy.GetParameterAsText(1))
c = c + "\\"
#Calcula a direção de fluxo
arcpy.env.addOutputsToMap = "true"
arcpy.gp.FlowDirection_sa(x, c + "fdr.tif","NORMAL","#")
#Calcula o acumulo de fluxo
arcpy.gp.FlowAccumulation_sa("fdr.tif", c + "fcc.tif",x,"FLOAT")
#Delimita a rede de drenagem a partir do valor CON
arcpy.gp.RasterCalculator_sa("""Con("fcc.tif" >  80000000,1)""",c + "calc.tif")
#Exporta a drenagem gerada em SHP
arcpy.gp.StreamToFeature_sa("calc.tif","fdr.tif",c + "drenagem.shp","SIMPLIFY")
#Deleta arquivos intermediários
if Exists(c + "fdr.tif"):
    Delete_management(c + "fdr.tif")
    Delete_management(c + "fcc.tif")
    Delete_management(c + "calc.tif")
#Limpa os campos desnecessários
DeleteField_management("drenagem", "FROM_NODE")
DeleteField_management("drenagem", "GRID_CODE")
DeleteField_management("drenagem", "TO_NODE")
#Simplifica a drenagem a partir de um valor determinado
SimplifyLine_cartography("drenagem", c + "simplify","POINT_REMOVE","200 Meters")
#Adiciona o campo de comprimento nas camadas
AddGeometryAttributes_management("simplify","LENGTH","METERS", "", sr)
AddGeometryAttributes_management("drenagem","LENGTH","METERS", "", sr)
JoinField_management("drenagem","ARCID", "simplify","ARCID","LENGTH")
#Adiciona campo de Sinuosidade e o calcula
AddField_management("drenagem", "sinuosity", "DOUBLE")
CalculateField_management("drenagem", "sinuosity", "[LENGTH]/[LENGTH_1]")
#Adiciona a classificação para os niveis de sinuosidade
AddField_management("drenagem", "class_sinu", "TEXT")
SelectLayerByAttribute_management("drenagem", "NEW_SELECTION", '"sinuosity" > 0.99 AND "sinuosity" < 1.05')
CalculateField_management("drenagem","class_sinu", """ "quase reto" """)
SelectLayerByAttribute_management("drenagem", "NEW_SELECTION", '"sinuosity" > 1.05 AND "sinuosity" < 1.25')
CalculateField_management("drenagem","class_sinu", """ "enrolado" """)
SelectLayerByAttribute_management("drenagem", "NEW_SELECTION", '"sinuosity" > 1.25 AND "sinuosity" < 1.50')
CalculateField_management("drenagem","class_sinu", """ "torcido" """)
SelectLayerByAttribute_management("drenagem", "NEW_SELECTION", '"sinuosity" > 1.50')
CalculateField_management("drenagem","class_sinu", """ "meandrante" """)
SelectLayerByAttribute_management("drenagem", "CLEAR_SELECTION")
#Gera os verticies no inicio e no final da rede de drenagem
FeatureVerticesToPoints_management("drenagem", c + "pontos_end", "END")
FeatureVerticesToPoints_management("drenagem", c + "pontos_start", "START")
InterpolateShape_3d(x,"pontos_end", c + "pontos_interpolados_end", "", "1", "BILINEAR","DENSIFY","0")
InterpolateShape_3d(x,"pontos_start", c + "pontos_interpolados_start", "", "1", "BILINEAR","DENSIFY","0")
#Calcula a altimetria do início e fim dos pontos
AddGeometryAttributes_management("pontos_interpolados_end", "POINT_X_Y_Z_M", "","", sr)
DeleteField_management("pontos_interpolados_end","POINT_X")
DeleteField_management("pontos_interpolados_end","POINT_Y")
DeleteField_management("pontos_interpolados_end","POINT_M")
AddGeometryAttributes_management("pontos_interpolados_start", "POINT_X_Y_Z_M", "","", sr)
DeleteField_management("pontos_interpolados_start","POINT_X")
DeleteField_management("pontos_interpolados_start","POINT_Y")
DeleteField_management("pontos_interpolados_start","POINT_M")
#Dá join nos pontos com a drenagem
JoinField_management("drenagem","ARCID", "pontos_interpolados_start","ARCID","POINT_Z")
JoinField_management("drenagem","ARCID", "pontos_interpolados_end","ARCID","POINT_Z")
#Adiciona e calcula a variação altimétrica
AddField_management("drenagem", "var_altime", "DOUBLE")
CalculateField_management("drenagem", "var_altime", "[POINT_Z] - [POINT_Z_1]")
#Deleta os campos desnecessários
DeleteField_management("drenagem", "POINT_Z")
DeleteField_management("drenagem", "POINT_Z_1")
#Deleta os arquivos intermediários
Delete_management("pontos_end")
Delete_management("pontos_start")
Delete_management("simplify_Pnt")
Delete_management("simplify")
Delete_management("pontos_interpolados_start")
Delete_management("pontos_interpolados_end")
