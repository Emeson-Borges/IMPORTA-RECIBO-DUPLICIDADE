# Atualizar Recibos do Evento S1200 -> eSocial

## Faça a consulta no banco de dados
`select idevento,cpftrab from esocial.s1200 where idevento in (select IDEVENTO from esocial.historico where status='A')`

pegue o resultado e coloque na lista dentro do Script em Python.

`lista_ids_cpfs = [`

 `   ("IDEVENTO", "CPF"),`

`]`