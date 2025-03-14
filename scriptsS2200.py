import os
import xml.etree.ElementTree as ET

def ns(tag, namespace):
    """Adiciona o namespace ao caminho do elemento."""
    return f"{{{namespace}}}{tag}"

def buscar_informacoes_por_cpf(caminho_arquivo, cpf, namespace_main, namespace_evt, namespace_retorno):
    try:
        tree = ET.parse(caminho_arquivo)
        root = tree.getroot()
        
        # Buscar o nó <evento> dentro do XML
        evento = root.find(f".//{ns('retornoProcessamentoDownload', namespace_main)}/{ns('evento', namespace_main)}/{ns('eSocial', namespace_evt)}/{ns('evtAdmissao', namespace_evt)}")
        recibo = root.find(f".//{ns('retornoProcessamentoDownload', namespace_main)}/{ns('recibo', namespace_main)}/{ns('eSocial', namespace_retorno)}/{ns('retornoEvento', namespace_retorno)}/{ns('recibo', namespace_retorno)}/{ns('nrRecibo', namespace_retorno)}")
        
        if evento is None:
            print(f"Erro: Evento não encontrado no arquivo {caminho_arquivo}")
            return None
        
        cpf_xml = evento.find(f".//{ns('trabalhador', namespace_evt)}/{ns('cpfTrab', namespace_evt)}")
        
        if cpf_xml is not None and cpf_xml.text == cpf:
            id_evento_novo = evento.attrib.get("Id")
            nr_recibo_text = recibo.text if recibo is not None else "NR_RECIBO_NAO_ENCONTRADO"
            return id_evento_novo, nr_recibo_text, cpf_xml.text
        return None
    except ET.ParseError:
        print(f"Erro ao analisar o arquivo XML: {caminho_arquivo}")
        return None
    except Exception as e:
        print(f"Erro ao processar o arquivo XML {caminho_arquivo}: {str(e)}")
        return None

def processar_lista_cpfs(lista_ids_cpfs, caminho_pasta_xml, namespace_main, namespace_evt, namespace_retorno):
    resultados = []
    
    for id_antigo, cpf in lista_ids_cpfs:
        for arquivo in os.listdir(caminho_pasta_xml):
            if arquivo.endswith(".xml"):
                caminho_completo = os.path.join(caminho_pasta_xml, arquivo)
                informacoes = buscar_informacoes_por_cpf(caminho_completo, cpf, namespace_main, namespace_evt, namespace_retorno)
                
                if informacoes is not None:
                    id_evento_novo, nr_recibo, cpf_encontrado = informacoes
                    resultados.append((id_evento_novo, nr_recibo, cpf_encontrado, id_antigo))
                    break  # Sai do loop quando encontrar o CPF
    return resultados

def salvar_resultados_em_txt(resultados, caminho_arquivo_txt):
    with open(caminho_arquivo_txt, "w") as f:
        for resultado in resultados:
            f.write(
                f"update esocial.s2200 set idevento='{resultado[0]}', situacao='1' where cpftrab='{resultado[2]}' and idevento='{resultado[3]}';\n\n"
            )
            f.write(
                f"update esocial.historico set idevento='{resultado[0]}', nr_recibo='{resultado[1]}', message='201 - Lote processado com sucesso', status='P' where idevento='{resultado[3]}' AND evento='S2200';\n\n"
            )

# Namespaces do XML
namespace_main = "http://www.esocial.gov.br/schema/download/retornoProcessamento/v1_0_0"
namespace_evt = "http://www.esocial.gov.br/schema/evt/evtAdmissao/v_S_01_03_00"
namespace_retorno = "http://www.esocial.gov.br/schema/evt/retornoEvento/v1_2_1"

# Lista de IDs antigos e CPFs fornecida
lista_ids_cpfs = [
# ('IDEVENTO',	'CPFTRAB'),



]

# Caminho para a pasta contendo os arquivos XML
caminho_pasta_xml = "C:/Users/itarg/Downloads/xml-PMAnapu-Separado/S-2200"

# Processar a lista e obter os resultados
resultados = processar_lista_cpfs(lista_ids_cpfs, caminho_pasta_xml, namespace_main, namespace_evt, namespace_retorno)

# Caminho para salvar o arquivo TXT com os resultados
caminho_arquivo_txt = "C:/Users/itarg/Downloads/SCRIPT-SQL2200.txt"

# Salvar os resultados em um arquivo TXT
salvar_resultados_em_txt(resultados, caminho_arquivo_txt)

print("Processamento concluído. Verifique o arquivo de saída.")
