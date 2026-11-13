package com.dhuadapter;
import android.view.*;import android.widget.*;
/** Repair only the hidden legacy toolbar anchor; ordinary Compose/pop-up anchors are untouched. */
public final class MenuAnchorFix {
 public static View resolve(View anchor){
  if(anchor==null||anchor.getWidth()>0&&anchor.getHeight()>0&&anchor.isShown())return anchor;
  boolean toolbar=false;View v=anchor;
  while(v!=null){try{if("main_toolbar".equals(v.getResources().getResourceEntryName(v.getId())))toolbar=true;}catch(Exception ignored){}v=v.getParent() instanceof View?(View)v.getParent():null;}
  if(!toolbar)return anchor;
  View root=anchor.getRootView();if(!(root instanceof FrameLayout)||!root.isAttachedToWindow())return anchor;
  final String tag="e8-legacy-menu-anchor";View target=root.findViewWithTag(tag);
  if(target==null){target=new View(anchor.getContext());target.setTag(tag);target.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);target.setClickable(false);((FrameLayout)root).addView(target);}
  float dp=anchor.getResources().getDisplayMetrics().density;int top=0;
  if(root.getRootWindowInsets()!=null)top=root.getRootWindowInsets().getStableInsetTop();
  FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(1,1,Gravity.TOP|Gravity.RIGHT);lp.rightMargin=Math.round(24*dp);lp.topMargin=top+Math.round(72*dp);target.setLayoutParams(lp);
  target.measure(View.MeasureSpec.makeMeasureSpec(1,View.MeasureSpec.EXACTLY),View.MeasureSpec.makeMeasureSpec(1,View.MeasureSpec.EXACTLY));int x=root.getWidth()-lp.rightMargin-1;target.layout(x,lp.topMargin,x+1,lp.topMargin+1);
  return target;
 }
}
