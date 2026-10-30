-- =====================================================================
-- GLPI ITIL PROCESS CONFIGURATION - PROJETO X / INSTANA TURBO
-- =====================================================================

-- 1. GRUPOS ITIL (Estrutura de Atendimento e Governança)
INSERT INTO `glpi_groups` (`name`, `completename`, `comment`, `is_assign`, `is_requester`, `is_watcher`, `is_task`, `is_notify`, `is_itemgroup`, `date_creation`) VALUES
('N1 - Central de Serviços (Service Desk)', 'N1 - Central de Serviços (Service Desk)', 'Triagem, primeiro atendimento e escalonamento ITIL', 1, 1, 1, 1, 1, 1, NOW()),
('N2 - Suporte a Aplicações & AIOps', 'N2 - Suporte a Aplicações & AIOps', 'Diagnóstico técnico, incidentes de microsserviços e alertas Instana', 1, 1, 1, 1, 1, 1, NOW()),
('N3 - Engenharia de Infraestrutura & Cloud', 'N3 - Engenharia de Infraestrutura & Cloud', 'Sustentação de bare-metal, virtualização, clusters e banco de dados', 1, 1, 1, 1, 1, 1, NOW()),
('Comitê de Mudanças (CAB - Change Advisory Board)', 'Comitê de Mudanças (CAB - Change Advisory Board)', 'Avaliação e aprovação de Mudanças (RFCs) conforme processo ITIL', 1, 1, 1, 1, 1, 1, NOW()),
('Gestão de Problemas (Problem Management & RCA)', 'Gestão de Problemas (Problem Management & RCA)', 'Investigação de Causa Raiz, Erros Conhecidos (KEDB) e Soluções de Contorno', 1, 1, 1, 1, 1, 1, NOW())
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- 2. CATEGORIAS ITIL (Taxonomia de Serviços e Incidentes)
INSERT INTO `glpi_itilcategories` (`name`, `completename`, `level`, `is_incident`, `is_request`, `is_problem`, `is_change`, `is_helpdeskvisible`, `date_creation`) VALUES
('Infraestrutura', 'Infraestrutura', 1, 1, 1, 1, 1, 1, NOW()),
('Plataformas & Cloud', 'Plataformas & Cloud', 1, 1, 1, 1, 1, 1, NOW()),
('Aplicações & Negócio', 'Aplicações & Negócio', 1, 1, 1, 1, 1, 1, NOW()),
('AIOps & Observabilidade', 'AIOps & Observabilidade', 1, 1, 1, 1, 1, 1, NOW()),
('Segurança da Informação', 'Segurança da Informação', 1, 1, 1, 1, 1, 1, NOW());

SET @cat_infra = (SELECT id FROM glpi_itilcategories WHERE name = 'Infraestrutura' AND level = 1 LIMIT 1);
SET @cat_plat  = (SELECT id FROM glpi_itilcategories WHERE name = 'Plataformas & Cloud' AND level = 1 LIMIT 1);
SET @cat_app   = (SELECT id FROM glpi_itilcategories WHERE name = 'Aplicações & Negócio' AND level = 1 LIMIT 1);
SET @cat_aiops = (SELECT id FROM glpi_itilcategories WHERE name = 'AIOps & Observabilidade' AND level = 1 LIMIT 1);
SET @cat_sec   = (SELECT id FROM glpi_itilcategories WHERE name = 'Segurança da Informação' AND level = 1 LIMIT 1);

INSERT INTO `glpi_itilcategories` (`itilcategories_id`, `name`, `completename`, `level`, `is_incident`, `is_request`, `is_problem`, `is_change`, `is_helpdeskvisible`, `date_creation`) VALUES
(@cat_infra, 'Servidores & Computação', 'Infraestrutura > Servidores & Computação', 2, 1, 1, 1, 1, 1, NOW()),
(@cat_infra, 'Redes & Conectividade', 'Infraestrutura > Redes & Conectividade', 2, 1, 1, 1, 1, 1, NOW()),
(@cat_infra, 'Storage & Backup', 'Infraestrutura > Storage & Backup', 2, 1, 1, 1, 1, 1, NOW()),

(@cat_plat, 'Kubernetes & Containers', 'Plataformas & Cloud > Kubernetes & Containers', 2, 1, 1, 1, 1, 1, NOW()),
(@cat_plat, 'Banco de Dados & Cache', 'Plataformas & Cloud > Banco de Dados & Cache', 2, 1, 1, 1, 1, 1, NOW()),

(@cat_app, 'Microsserviços & APIs', 'Aplicações & Negócio > Microsserviços & APIs', 2, 1, 1, 1, 1, 1, NOW()),
(@cat_app, 'Portais Web & UI', 'Aplicações & Negócio > Portais Web & UI', 2, 1, 1, 1, 1, 1, NOW()),

(@cat_aiops, 'Instana - Incidentes Críticos (AIOps)', 'AIOps & Observabilidade > Instana - Incidentes Críticos (AIOps)', 2, 1, 0, 1, 1, 1, NOW()),
(@cat_aiops, 'Instana - Degradação & Anomalias (AIOps)', 'AIOps & Observabilidade > Instana - Degradação & Anomalias (AIOps)', 2, 1, 0, 1, 1, 1, NOW()),
(@cat_aiops, 'Instana - Eventos de Mudança de Host', 'AIOps & Observabilidade > Instana - Eventos de Mudança de Host', 2, 0, 0, 0, 1, 1, NOW()),

(@cat_sec, 'Certificados Digitais & TLS', 'Segurança da Informação > Certificados Digitais & TLS', 2, 1, 1, 1, 1, 1, NOW()),
(@cat_sec, 'Vulnerabilidades & Patches', 'Segurança da Informação > Vulnerabilidades & Patches', 2, 1, 1, 1, 1, 1, NOW());

-- 3. ACORDOS DE NÍVEL DE SERVIÇO ITIL (SLAs)
INSERT INTO `glpi_slas` (`name`, `type`, `number_time`, `definition_time`, `comment`, `date_creation`) VALUES
('SLA Resposta P1 - Crítico (Instana/NOC)', 0, 15, 'minute', 'Tempo de resposta de 15 minutos para incidentes críticos Instana/NOC', NOW()),
('SLA Resposta P2 - Alto', 0, 30, 'minute', 'Tempo de resposta de 30 minutos para incidentes de alto impacto', NOW()),
('SLA Resposta P3 - Médio', 0, 2, 'hour', 'Tempo de resposta de 2 horas para incidentes médios', NOW()),
('SLA Resposta P4 - Baixo', 0, 4, 'hour', 'Tempo de resposta de 4 horas para incidentes baixos', NOW()),
('SLA Resposta P5 - Planejado', 0, 8, 'hour', 'Tempo de resposta de 8 horas para demandas planejadas', NOW()),

('SLA Solução P1 - Crítico (Instana/NOC)', 1, 2, 'hour', 'Resolução de 2 horas para incidentes críticos com parada de serviço', NOW()),
('SLA Solução P2 - Alto', 1, 4, 'hour', 'Resolução de 4 horas para incidentes de alta prioridade', NOW()),
('SLA Solução P3 - Médio', 1, 8, 'hour', 'Resolução de 8 horas para incidentes de média prioridade', NOW()),
('SLA Solução P4 - Baixo', 1, 24, 'hour', 'Resolução de 24 horas para incidentes baixos', NOW()),
('SLA Solução P5 - Planejado', 1, 72, 'hour', 'Resolução de 72 horas para demandas planejadas', NOW())
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- 4. CMDB - ITEM DE CONFIGURAÇÃO (Servidor Monitorado pelo Instana)
INSERT INTO `glpi_computers` (`name`, `serial`, `comment`, `date_creation`) VALUES
('192.168.173.22 - Luciano GPU Server', 'GPU-SRV-01', 'Servidor de Produção monitorado pelo IBM Instana Agent (Zone: Luciano-GPU-Production)', NOW())
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);
