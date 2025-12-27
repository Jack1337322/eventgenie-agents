from chains.budget_chain import BudgetChain
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FinanceAgent:
    """
    Finance Agent - calculates budgets using GigaChat with budget constraints
    """
    
    def __init__(self):
        self.chain = BudgetChain()
        logger.info("Finance Agent initialized")
    
    async def calculate_budget(self, event_data: dict) -> dict:
        """
        Calculate event budget with budget constraints
        """
        try:
            logger.info(f"Finance Agent: Calculating budget for {event_data.get('event_name')}")
            
            # Проверяем наличие общего бюджета
            total_budget = event_data.get('total_budget')
            if total_budget is None:
                logger.warning("Total budget not specified, calculations may exceed reasonable limits")
            
            # Добавляем информацию о приоритетах и ограничениях
            enhanced_event_data = event_data.copy()
            
            # Если есть ограничения по бюджету, добавляем их в запрос
            if 'budget_constraints' not in enhanced_event_data:
                enhanced_event_data['budget_constraints'] = {}
            
            # Добавляем общий бюджет в constraints
            if total_budget is not None:  # ← было if total_budget
                enhanced_event_data['budget_constraints']['total'] = total_budget
            
            result = await self.chain.calculate_budget(enhanced_event_data)
            
            # Проверяем, не превышен ли бюджет
            if total_budget is not None and 'total_cost' in result:  # ← было if total_budget
                total_cost = result['total_cost']
                if total_cost > total_budget:
                    # --- новый минимальный блок: принудительно ужимаем бюджет ---
                    ratio = total_budget / total_cost if total_cost > 0 else 0

                    # Масштабируем categories, если есть
                    if 'categories' in result and isinstance(result['categories'], list):
                        for cat in result['categories']:
                            if isinstance(cat, dict) and 'amount' in cat:
                                amount = cat.get('amount') or 0
                                cat['amount'] = amount * ratio

                    # Масштабируем category_details, если есть
                    if 'category_details' in result and isinstance(result['category_details'], dict):
                        for cat in result['category_details'].values():
                            if isinstance(cat, dict) and 'amount' in cat:
                                amount = cat.get('amount') or 0
                                cat['amount'] = amount * ratio

                    # Фиксируем итоговую стоимость ровно в лимит
                    result['total_cost'] = total_budget
                    result['budget_status'] = 'within_budget'
                else:
                    result['budget_status'] = 'within_budget'
                    remaining = total_budget - total_cost
                    result['recommendations'].append(
                        f"✅ Бюджет в пределах лимита. Остаток: {remaining:.2f} руб."
                    )
            
            # Обеспечиваем детализацию категорий
            if 'categories' in result and isinstance(result['categories'], list):
                detailed_categories = []
                for i, category in enumerate(result['categories']):
                    if isinstance(category, dict):
                        # Дополняем информацию о категории
                        detailed_category = {
                            'id': i + 1,
                            'name': category.get('name', f'Категория {i+1}'),
                            'description': category.get('description', ''),
                            'amount': category.get('amount', 0),
                            'percentage': category.get('percentage', 0),
                            'subcategories': category.get('subcategories', []),
                            'priority': category.get('priority', 'medium'),
                            'notes': category.get('notes', ''),
                            'is_flexible': category.get('is_flexible', True)
                        }
                        detailed_categories.append(detailed_category)
                
                result['detailed_categories'] = detailed_categories
                
                # Добавляем детальную сводку по категориям
                if 'analysis' not in result:
                    result['analysis'] = ''
                
                category_summary = "\nДетализация расходов по категориям:\n"
                for cat in detailed_categories:
                    category_summary += (
                        f"{cat['id']}. {cat['name']}: {cat['amount']:.2f} руб. "
                        f"({cat['percentage']:.1f}% бюджета)\n"
                    )
                    if cat.get('subcategories'):
                        for sub in cat['subcategories']:
                            if isinstance(sub, dict):
                                category_summary += f"   - {sub.get('name')}: {sub.get('amount', 0):.2f} руб.\n"
                
                result['analysis'] += category_summary
            
            logger.info(f"Finance Agent: Budget calculated successfully. "
                       f"Status: {result.get('budget_status', 'unknown')}")
            
            # Добавляем временные метки для отслеживания
            result['calculation_timestamp'] = datetime.datetime.now().isoformat()
            result['budget_version'] = '1.0'
            
            return result
            
        except Exception as e:
            logger.error(f"Finance Agent error: {e}", exc_info=True)
            # Возвращаем структурированную ошибку
            return {
                'error': str(e),
                'categories': [],
                'total_cost': 0,
                'budget_status': 'error',
                'analysis': 'Произошла ошибка при расчете бюджета',
                'recommendations': ['Обратитесь к администратору системы'],
                'detailed_categories': []
            }

# Добавляем импорт datetime для временных меток
import datetime
