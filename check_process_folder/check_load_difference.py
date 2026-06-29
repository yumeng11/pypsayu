import pypsa
import pandas as pd
import matplotlib.pyplot as plt
import os

def compare_and_save_de_loads(path1, path2, output_dir, label1="Base", label2="Warming"):

    n1 = pypsa.Network(path1)
    n2 = pypsa.Network(path2)

    de_loads1 = n1.loads.index[n1.loads.bus.str.contains("DE")]
    de_loads2 = n2.loads.index[n2.loads.bus.str.contains("DE")]

    load_de1 = n1.loads_t.p_set[de_loads1].sum(axis=1)
    load_de2 = n2.loads_t.p_set[de_loads2].sum(axis=1)

    total1 = load_de1.sum() / 1e6  # TWh
    total2 = load_de2.sum() / 1e6
    diff_total = (total2 - total1) / total1 * 100

    # 5. 绘图
    plt.figure(figsize=(15, 7))
    load_de1.iloc[:336].plot(label=f"{label1} ({total1:.1f} TWh)", alpha=0.8)
    load_de2.iloc[:336].plot(label=f"{label2} ({total2:.1f} TWh)", linestyle='--', alpha=0.8)
    
    plt.title(f"Germany Load Comparison: {label1} vs {label2} (Total Diff: {diff_total:+.2f}%)")
    plt.xlabel("Time")
    plt.ylabel("Power [MW]")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 6. 保存图片
    save_path = os.path.join(output_dir, f"DE_load_comparison_{label2}.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close() # 关闭画布，防止内存占用

    # print(f"--- 对比完成 ---")
    print(f"图片已保存至: {save_path}")
    # print(f"总用电量变化: {diff_total:+.2f}%")

# --- 参数配置 ---
path_base = "/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/networks/base_s_512_elec_.nc"
path_warm = "/gpfs1/data/compoundx/yumeng/paper2/pypsa_output/warming2_s0_weather_year_2015/networks/base_s_512_elec_.nc"
# 你要求的保存路径
plot_folder = "/gpfs1/data/compoundx/yumeng/project_code/pypsa-eur/check_process_folder/plots"

# 执行
compare_and_save_de_loads(path_base, path_warm, plot_folder, "Base", "Warming_2015")