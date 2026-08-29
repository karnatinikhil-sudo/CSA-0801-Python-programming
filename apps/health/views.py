import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Medicine, MedicineLog, WellnessTip, HydrationLog
from .forms import MedicineForm
from apps.accounts.models import UserProfile

def get_wellness_card_context(user):
    """Computes all data needed for the central Dashboard Health & Wellness card."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.check_and_reset_daily_water()

    today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
    now_time = datetime.datetime.now().time()
    
    # 1. Rotating Tip
    tips = list(WellnessTip.objects.filter(is_active=True).order_by('id'))
    current_tip = None
    if tips:
        idx = profile.last_tip_index % len(tips)
        current_tip = tips[idx]

    # 2. Hydration & WHO Guidelines metrics
    who_glasses, who_liters, who_explanation = profile.calculate_who_recommended_water_glasses()
    # Update water_daily_target if not manually set or zero
    if profile.water_daily_target != who_glasses:
        water_target = profile.water_daily_target
    else:
        water_target = who_glasses
        
    water_count = profile.water_intake_today
    water_target = max(1, water_target)
    water_percent = min(100, int((water_count / water_target) * 100))
    adaptive_interval = profile.calculate_adaptive_hydration_interval_minutes()

    # 3. Active Medicines & Today's Schedule
    user_medicines = Medicine.objects.filter(user=user, is_active=True)
    has_medicines = user_medicines.exists()
    
    todays_doses = []
    if has_medicines:
        for med in user_medicines:
            if med.is_currently_active():
                for t_str in med.scheduled_times:
                    # Check if logged for today
                    log = MedicineLog.objects.filter(
                        medicine=med,
                        scheduled_date=today,
                        scheduled_time=t_str
                    ).first()
                    
                    # Convert t_str to time object to determine if due/upcoming/past
                    try:
                        dose_t = datetime.time.fromisoformat(t_str)
                        is_past = dose_t <= now_time
                    except ValueError:
                        is_past = False

                    todays_doses.append({
                        'medicine_id': med.id,
                        'name': med.name,
                        'dosage': med.dosage,
                        'time': t_str,
                        'notes': med.notes,
                        'status': log.status if log else ('DUE' if is_past else 'UPCOMING'),
                        'log': log,
                    })

        # Sort doses by time
        todays_doses.sort(key=lambda x: x['time'])

    # 4. 7-Day Adherence Calculation
    seven_days_ago = today - datetime.timedelta(days=7)
    past_logs = MedicineLog.objects.filter(
        user=user,
        scheduled_date__gte=seven_days_ago,
        scheduled_date__lte=today
    )
    total_logged_doses = past_logs.count()
    taken_doses = past_logs.filter(status='TAKEN').count()
    
    adherence_rate = int((taken_doses / total_logged_doses * 100)) if total_logged_doses > 0 else 100
    adherence_summary = f"You've taken {taken_doses} of {total_logged_doses} doses this week" if total_logged_doses > 0 else "All caught up on meds"

    return {
        'profile': profile,
        'current_tip': current_tip,
        'water_count': water_count,
        'water_target': water_target,
        'water_percent': water_percent,
        'who_glasses': who_glasses,
        'who_liters': who_liters,
        'who_explanation': who_explanation,
        'adaptive_interval': adaptive_interval,
        'has_medicines': has_medicines,
        'medicines': user_medicines,
        'todays_doses': todays_doses,
        'adherence_rate': adherence_rate,
        'adherence_summary': adherence_summary,
        'taken_doses': taken_doses,
        'total_logged_doses': total_logged_doses,
    }


@login_required
def medicine_list_view(request):
    medicines = Medicine.objects.filter(user=request.user)
    context = {
        'medicines': medicines,
        'wellness': get_wellness_card_context(request.user),
    }
    return render(request, 'health/medicines.html', context)


@login_required
def medicine_create_view(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.user = request.user
            med.save()
            messages.success(request, f'Medication "{med.name}" schedule added!')
            return redirect('health:medicines')
    else:
        form = MedicineForm()

    return render(request, 'health/medicine_form.html', {'form': form, 'title': 'Add Medication Schedule'})


@login_required
def medicine_edit_view(request, pk):
    med = get_object_or_404(Medicine, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            messages.success(request, f'Medication "{med.name}" updated successfully!')
            return redirect('health:medicines')
    else:
        form = MedicineForm(instance=med)

    return render(request, 'health/medicine_form.html', {'form': form, 'med': med, 'title': 'Edit Medication'})


@login_required
@require_POST
def medicine_delete_view(request, pk):
    med = get_object_or_404(Medicine, pk=pk, user=request.user)
    name = med.name
    med.delete()
    messages.info(request, f'Medication "{name}" removed from your list.')
    return redirect('health:medicines')


@login_required
@require_POST
def log_water_intake_ajax(request):
    """Increment water intake count (+1 glass) and create timestamped log."""
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.check_and_reset_daily_water()

        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        action = data.get('action', 'add')

        if action == 'add':
            profile.water_intake_today += 1
            profile.last_water_logged_at = timezone.now()
            profile.save(update_fields=['water_intake_today', 'last_water_logged_at'])
            HydrationLog.objects.create(user=request.user, glasses=1)
        elif action == 'reset':
            profile.water_intake_today = 0
            profile.save(update_fields=['water_intake_today'])

        target = max(1, profile.water_daily_target)
        percent = min(100, int((profile.water_intake_today / target) * 100))

        return JsonResponse({
            'success': True,
            'water_count': profile.water_intake_today,
            'water_target': target,
            'water_percent': percent,
            'message': 'Great job staying hydrated! 💧'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def next_wellness_tip_ajax(request):
    """Rotates to next wellness tip and saves index on user profile."""
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        tips = list(WellnessTip.objects.filter(is_active=True).order_by('id'))
        if not tips:
            return JsonResponse({'success': False, 'error': 'No tips available'})

        profile.last_tip_index = (profile.last_tip_index + 1) % len(tips)
        profile.save(update_fields=['last_tip_index'])
        next_tip = tips[profile.last_tip_index]

        return JsonResponse({
            'success': True,
            'tip': {
                'id': next_tip.id,
                'title': next_tip.title,
                'tip_text': next_tip.tip_text,
                'category': next_tip.get_category_display(),
                'icon': next_tip.icon,
                'action_label': next_tip.action_label,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def log_medicine_action_ajax(request):
    """
    Records action on a scheduled medication dose:
    action: 'TAKEN' | 'SKIPPED' | 'SNOOZE'
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        med_id = data.get('medicine_id')
        time_str = data.get('time')
        action = data.get('action', 'TAKEN').upper()
        
        medicine = get_object_or_404(Medicine, pk=med_id, user=request.user)
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()

        if action == 'SNOOZE':
            # Handle 15 min snooze
            return JsonResponse({
                'success': True,
                'status': 'SNOOZED',
                'message': f'Reminder for {medicine.name} snoozed for 15 minutes.'
            })

        log, created = MedicineLog.objects.update_or_create(
            medicine=medicine,
            scheduled_date=today,
            scheduled_time=time_str,
            defaults={
                'user': request.user,
                'status': action,
                'logged_at': timezone.now()
            }
        )

        # Recalculate 7-day adherence
        seven_days_ago = today - datetime.timedelta(days=7)
        past_logs = MedicineLog.objects.filter(
            user=request.user,
            scheduled_date__gte=seven_days_ago,
            scheduled_date__lte=today
        )
        total_doses = past_logs.count()
        taken_doses = past_logs.filter(status='TAKEN').count()
        adherence_rate = int((taken_doses / total_doses * 100)) if total_doses > 0 else 100
        summary_text = f"You've taken {taken_doses} of {total_doses} doses this week ({adherence_rate}%)"

        return JsonResponse({
            'success': True,
            'medicine_id': medicine.id,
            'time': time_str,
            'status': action,
            'adherence_rate': adherence_rate,
            'adherence_summary': summary_text,
            'message': f'{medicine.name} marked as {action.capitalize()}!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
